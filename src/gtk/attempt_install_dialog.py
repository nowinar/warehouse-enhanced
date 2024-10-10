from gi.repository import Adw, Gtk
from .host_info import HostInfo
from .error_toast import ErrorToast

@Gtk.Template(resource_path="/io/github/flattool/Warehouse/gtk/attempt_install_dialog.ui")
class AttemptInstallDialog(Adw.AlertDialog):
	__gtype_name__ = "AttemptInstallDialog"
	gtc = Gtk.Template.Child
	
	preferences_group = gtc()
	
	def generate_list(self):
		for installation, remotes in HostInfo.remotes.items():
			for remote in remotes:
				if remote.disabled:
					continue
					
				row = Adw.ActionRow(title=remote.title, subtitle=_("Installation: {}").format(installation))
				row.remote_name = remote.name
				row.remote_installation = installation
				button = Gtk.CheckButton()
				row.add_prefix(button)
				row.check_button = button
				row.set_activatable_widget(button)
				self.rows.append(row)
				self.preferences_group.add(row)
				if len(self.rows) > 1:
					button.set_group(self.rows[0].check_button)
				else:
					button.activate()
					
	def on_response(self, dialog, response):
		if response != "continue":
			return
			
		for row in self.rows:
			if row.check_button.get_active():
				self.callback(row.remote_installation, row.remote_name)
				return
				
	def __init__(self, callback, **kwargs):
		super().__init__(**kwargs)
		
		# Extra Object Creation
		self.rows = []
		self.callback = callback
		
		# Apply
		self.generate_list()
		if len(self.rows) == 1:
			self.set_extra_child(None)
		elif len(self.rows) < 1:
			HostInfo.main_window.toast_overlay.add_toast(ErrorToast(_("Can't find matching packages"), _("Your system has no remotes added")).toast)
			
		self.present(HostInfo.main_window)
		
		# Connections
		self.connect("response", self.on_response)
