from gi.repository import Adw, Gtk, GLib, Gio
from .host_info import HostInfo
from .error_toast import ErrorToast
from .app_row import AppRow
from .snapshots_list_page import SnapshotsListPage
from .sidebar_button import SidebarButton
from .loading_status import LoadingStatus
from .new_snapshot_dialog import NewSnapshotDialog
import os, subprocess

class LeftoverSnapshotRow(Adw.ActionRow):
    __gtype_name__ = "LeftoverSnapshotRow"

    def idle_stuff(self):
        self.set_title(self.name)
        icon = Gtk.Image.new_from_icon_name("application-x-executable-symbolic")
        icon.set_icon_size(Gtk.IconSize.LARGE)
        self.add_prefix(icon)
        self.add_suffix(self.check_button)

    def __init__(self, folder, **kwargs):
        super().__init__(**kwargs)
        
        self.folder = folder
        self.set_activatable(True)
        self.name = self.folder.split('.')[-1]
        self.check_button = Gtk.CheckButton(visible=False)
        self.check_button.add_css_class("selection-mode")
        GLib.idle_add(lambda *_: self.idle_stuff())

@Gtk.Template(resource_path="/io/github/flattool/Warehouse/snapshot_page/snapshot_page.ui")
class SnapshotPage(Adw.BreakpointBin):
    __gtype_name__ = "SnapshotPage"
    gtc = Gtk.Template.Child

    toast_overlay = gtc()
    search_entry = gtc()
    search_bar = gtc()
    active_box = gtc()
    active_listbox = gtc()
    leftover_box = gtc()
    leftover_listbox = gtc()
    split_view = gtc()
    stack = gtc()
    no_snapshots = gtc()
    no_results = gtc()
    scrolled_window = gtc()
    open_button = gtc()
    status_open_button = gtc()
    status_new_button = gtc()
    new_button = gtc()
    status_stack = gtc()
    loading_view = gtc()
    snapshotting_view = gtc()

    # Referred to in the main window
    #    It is used to determine if a new page should be made or not
    #    This must be set to the created object from within the class's __init__ method
    instance = None
    page_name = "snapshots"

    def sort_snapshots(self, *args):
        self.active_snapshot_paks.clear()
        self.leftover_snapshots.clear()
        bad_folders = []

        if not os.path.exists(HostInfo.snapshots_path):
            try:
                os.makedirs(HostInfo.snapshots_path)
            except Exception as e:
                self.toast_overlay.add_toast(ErrorToast(_("Could not load Snapshots"), str(e)).toast)
                return
        
        for folder in os.listdir(HostInfo.snapshots_path):
            if folder.count('.') < 2 or ' ' in folder:
                bad_folders.append(folder)
                continue
            
            has_tar = False
            for file in os.listdir(f"{HostInfo.snapshots_path}{folder}"):
                if file.endswith(".tar.zst"):
                    has_tar = True
                    break
            
            if not has_tar:
                bad_folders.append(folder)
                continue

            try:
                pak = HostInfo.id_to_flatpak[folder]
                self.active_snapshot_paks.append(pak)
            except KeyError:
                self.leftover_snapshots.append(folder)

        for folder in bad_folders:
            try:
                subprocess.run(['gio', 'trash', f'{HostInfo.snapshots_path}{folder}'])
            except Exception:
                pass

    def generate_active_list(self):
        for pak in self.active_snapshot_paks:
            row = AppRow(pak)
            self.active_listbox.append(row)
            
        if len(self.active_snapshot_paks) > 0:
            self.active_box.set_visible(True)
            # first_row = self.active_listbox.get_row_at_index(0)
            # self.active_listbox.select_row(first_row)
        else:
            self.active_box.set_visible(False)

    def generate_leftover_list(self):
        for folder in self.leftover_snapshots:
            row = LeftoverSnapshotRow(folder)
            self.leftover_listbox.append(row)            

        if len(self.leftover_snapshots) > 0:
            self.leftover_box.set_visible(True)
            if len(self.active_snapshot_paks) == 0:
                self.stack.set_visible_child(self.scrolled_window)
                # first_row = self.leftover_listbox.get_row_at_index(0)
                # self.leftover_listbox.select_row(first_row)
        else:
            self.leftover_box.set_visible(False)

    def active_select_handler(self, listbox, row, should_show_content=True, refresh=False):
        self.leftover_listbox.select_row(None)
        self.list_page.set_snapshots(row.package, refresh)
        self.split_view.set_show_content(should_show_content)

    def leftover_select_handler(self, listbox, row, should_show_content=True, refresh=False):
        self.active_listbox.select_row(None)
        self.list_page.set_snapshots(row.folder, refresh)
        self.split_view.set_show_content(should_show_content)

    def select_first_row(self):
        if row := self.active_listbox.get_row_at_index(0):
            self.active_listbox.select_row(row)
            self.active_select_handler(None, row, False, True)
        elif row := self.leftover_listbox.get_row_at_index(0):
            self.leftover_listbox.select_row(row)
            self.leftover_select_handler(None, row, False, True)
            
    def show_snapshot(self, package):
        i = 0
        while row := self.active_listbox.get_row_at_index(i):
            i += 1
            if row.package is package:
                self.active_listbox.select_row(row)
                self.active_select_handler(None, row, True)
                self.toast_overlay.add_toast(Adw.Toast(title=_("Showing snapshots for {}").format(package.info['name'])))
                break
        else:
            dialog = NewSnapshotDialog(self, self.snapshotting_status, self.refresh, package)
            toast = Adw.Toast(title=_("No snapshots for {}").format(package.info['name']), button_label=_("New"))
            toast.connect("button-clicked", lambda *_: dialog.present(HostInfo.main_window))
            self.toast_overlay.add_toast(toast)

    def start_loading(self):
        self.status_stack.set_visible_child(self.loading_view)
        self.active_box.set_visible(True)
        self.active_listbox.remove_all()
        self.leftover_box.set_visible(True)
        self.leftover_listbox.remove_all()

    def end_loading(self):
        def callback(*args):
            self.new_snapshot_dialog = NewSnapshotDialog(self, self.snapshotting_status, self.refresh)
            self.generate_active_list()
            self.generate_leftover_list()
            if (not self.active_box.get_visible()) and (not self.leftover_box.get_visible()):
                GLib.idle_add(lambda *_: self.status_stack.set_visible_child(self.no_snapshots))
            else:
                self.select_first_row()
                GLib.idle_add(lambda *_: self.stack.set_visible_child(self.scrolled_window))
                GLib.idle_add(lambda *_: self.status_stack.set_visible_child(self.split_view))
                
        Gio.Task.new(None, None, callback).run_in_thread(self.sort_snapshots)

    def open_snapshots_folder(self, button):
        try:
            Gio.AppInfo.launch_default_for_uri(f"file://{HostInfo.snapshots_path}", None)
            self.toast_overlay.add_toast(Adw.Toast.new(_("Opened snapshots folder")))
        except Exception as e:
            self.toast_overlay.add_toast(ErrorToast(_("Could not open folder"), str(e)).toast)
            
    def on_cancel(self):
        for worker in self.new_snapshot_dialog.workers:
            worker.do_cancel("manual_cancel")
        
    def on_new(self, *args):
        self.new_snapshot_dialog.present(HostInfo.main_window)
        
    def refresh(self):
        self.start_loading()
        self.end_loading()
        
    def on_search(self, search_entry):
        text = search_entry.get_text().lower()
        i = 0
        total_active_visible = 0
        while row := self.active_listbox.get_row_at_index(i):
            i += 1
            row.set_visible(False)
            if text in row.get_title().lower():
                row.set_visible(True)
                total_active_visible += 1
        self.active_box.set_visible(total_active_visible > 0)
        
        i = 0
        total_leftover_visible = 0
        while row := self.leftover_listbox.get_row_at_index(i):
            i += 1
            row.set_visible(False)
            if text in row.get_title().lower():
                row.set_visible(True)
                total_leftover_visible += 1
        self.leftover_box.set_visible(total_leftover_visible > 0)
        
        if total_active_visible > 0 or total_leftover_visible > 0:
            self.stack.set_visible_child(self.scrolled_window)
        else:
            self.stack.set_visible_child(self.no_results)
            
    def sort_func(self, row1, row2):
        if type(row1) is AppRow:
            return row1.package.info['name'].lower() > row2.package.info['name'].lower()
        else:
            return row1.name.lower() > row2.name.lower()
        
    def __init__(self, main_window, **kwargs):
        super().__init__(**kwargs)
        
        # Extra Object Creation
        self.__class__.instance = self
        self.main_window = main_window
        self.active_snapshot_paks = []
        # self.active_rows = []
        self.leftover_snapshots = []
        # self.leftover_rows = []
        self.list_page = SnapshotsListPage(self)
        self.snapshotting_status = LoadingStatus("Initial Title", _("This might take a while"), True, self.on_cancel)
        
        # Connections
        self.active_listbox.connect("row-activated", self.active_select_handler)
        self.leftover_listbox.connect("row-activated", self.leftover_select_handler)
        self.open_button.connect("clicked", self.open_snapshots_folder)
        self.status_open_button.connect("clicked", self.open_snapshots_folder)
        self.status_new_button.connect("clicked", self.on_new)
        self.new_button.connect("clicked", self.on_new)
        self.search_entry.connect("search-changed", self.on_search)
        
        # Apply
        self.search_bar.set_key_capture_widget(HostInfo.main_window)
        self.loading_view.set_content(LoadingStatus(_("Loading Snapshots"), _("This should only take a moment")))
        self.snapshotting_view.set_content(self.snapshotting_status)
        self.snapshotting_status.button.set_label(_("Cancel"))
        self.split_view.set_content(self.list_page)
        self.active_listbox.set_sort_func(self.sort_func)
        self.leftover_listbox.set_sort_func(self.sort_func)
