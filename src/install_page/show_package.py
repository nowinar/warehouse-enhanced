from gi.repository import Adw, Gtk, GLib
from enum import Enum
import gettext
import requests
import bs4

_ = gettext.gettext


class PackageDetailsDialog(Gtk.Dialog):
	def __init__(self, parent, package):
		# Initialize the dialog with the parent window
		super().__init__(title=f"Package Details: {package.name}", transient_for=parent, use_header_bar=1, modal=True)
		print(package, dir(package))
		# Store the package reference
		self.package = package

		# Set dialog size
		self.set_default_size(500, 400)

		# Get the content area
		content_area = self.get_content_area()
		content_area.set_margin_top(24)
		content_area.set_margin_bottom(24)
		content_area.set_margin_start(24)
		content_area.set_margin_end(24)
		content_area.set_spacing(12)

		# Add package name header
		name_label = Gtk.Label(label=f"<b>{GLib.markup_escape_text(package.name)}</b>")
		name_label.set_use_markup(True)
		name_label.set_halign(Gtk.Align.START)
		name_label.set_margin_bottom(12)
		content_area.append(name_label)

		# Create package information rows
		info_group = Adw.PreferencesGroup()

		# App ID row
		app_id_row = Adw.ActionRow()
		app_id_row.set_title(_("App ID"))
		app_id_row.set_subtitle(package.app_id)

		# Version row
		version_row = Adw.ActionRow()
		version_row.set_title(_("Version"))
		version_row.set_subtitle(package.version)

		# Branch row
		branch_row = Adw.ActionRow()
		branch_row.set_title(_("Branch"))
		branch_row.set_subtitle(package.branch)

		# Add rows to the group
		info_group.add(app_id_row)
		info_group.add(version_row)
		info_group.add(branch_row)
		content_area.append(info_group)
		# Add action buttons to the dialog
		# self.add_button(_("Close"), Gtk.ResponseType.CLOSE)
		open_url_button = self.add_button(_("Open Flatpak URL"), Gtk.ResponseType.APPLY)
		open_url_button.add_css_class("suggested-action")

		# Connect the response signal
		self.connect("response", self.on_response)

	def on_response(self, dialog, response_id):
		if response_id == Gtk.ResponseType.APPLY:
			# Open Flatpak URL
			self.open_flatpak_url()
		self.destroy()

	def open_flatpak_url(self):
		# Construct the Flathub URL based on the app_id
		url = f"https://flathub.org/apps/{self.package.app_id}"

		# Open the URL in the default browser
		GLib.spawn_command_line_async(f"xdg-open '{url}'")

	def app_id(self):
		response = requests.get(f"https://flathub.org/apps/{self.package.app_id}")
		if response.status_code == 200:
			soup = bs4.BeautifulSoup(response.content, "html.parser")
			data = soup.find_all("div", class_="relative m-2 flex h-[128px] min-w-[128px] self-center drop-shadow-md")
			print(data[0].img["src"])


# Function to show package details
def show_package_details(self):
	dialog = PackageDetailsDialog(self.get_root(), self.package)
	dialog.present()


# class show_package_details(Gtk.Dialog):
#     def __init__(self, parent):
#         super().__init__(title="My Dialog", transient_for=self.get_root(), flags=0)
#         self.add_buttons(
#             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
#         )

#         self.set_default_size(150, 100)

#         label = Gtk.Label(label="This is a dialog to display additional information")

#         box = self.get_content_area()
#         box.add(label)
#         self.show_all()
# def show_package_details(self):
#     # Create a new dialog window
#     dialog = Adw.Dialog()
#     dialog.set_title(_("Package Details: {}").format(self.package.name))

#     # Create a content box for the dialog
#     content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
#     content_box.set_margin_top(24)
#     content_box.set_margin_bottom(24)
#     content_box.set_margin_start(24)
#     content_box.set_margin_end(24)
#     content_box.set_size_request(500, -1)

#     # Add package name header
#     name_label = Gtk.Label(
#         label=f"<b>{GLib.markup_escape_text(self.package.name)}</b>"
#     )
#     name_label.set_use_markup(True)
#     name_label.set_halign(Gtk.Align.START)
#     name_label.set_margin_bottom(12)

#     # Create package information rows
#     info_group = Adw.PreferencesGroup()

#     # App ID row
#     app_id_row = Adw.ActionRow()
#     app_id_row.set_title(_("App ID"))
#     app_id_row.set_subtitle(self.package.app_id)

#     # Version row
#     version_row = Adw.ActionRow()
#     version_row.set_title(_("Version"))
#     version_row.set_subtitle(self.package.version)

#     # Branch row
#     branch_row = Adw.ActionRow()
#     branch_row.set_title(_("Branch"))
#     branch_row.set_subtitle(self.package.branch)

#     # Add rows to the group
#     info_group.add(app_id_row)
#     info_group.add(version_row)
#     info_group.add(branch_row)

#     # Create action buttons
#     button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
#     button_box.set_halign(Gtk.Align.END)
#     button_box.set_margin_top(12)

#     # Open URL button
#     open_url_button = Gtk.Button(label=_("Open Flatpak URL"))
#     open_url_button.connect("clicked", lambda btn: open_flatpak_url(self))
#     open_url_button.add_css_class("suggested-action")

#     # Close button
#     close_button = Gtk.Button(label=_("Close"))
#     close_button.connect("clicked", lambda btn: dialog.close())

#     # Add buttons to button box
#     button_box.append(open_url_button)
#     button_box.append(close_button)

#     # Assemble the dialog content
#     content_box.append(name_label)
#     content_box.append(info_group)
#     content_box.append(button_box)

#     # Create a child for the dialog
#     dialog.set_child(content_box)
#     dialog.present()
