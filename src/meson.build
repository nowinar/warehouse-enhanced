pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'src')
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'gtk/app_row.blp',
    'gtk/help-overlay.blp',
    'gtk/loading_status.blp',
    'gtk/installation_chooser.blp',
    'gtk/attempt_install_dialog.blp',
    'main_window/window.blp',
    'packages_page/packages_page.blp',
    'packages_page/filters_page.blp',
    'packages_page/uninstall_dialog.blp',
    'properties_page/properties_page.blp',
    'user_data_page/data_box.blp',
    'user_data_page/user_data_page.blp',
    'user_data_page/data_subpage.blp',
    'remotes_page/remotes_page.blp',
    'remotes_page/remote_row.blp',
    'remotes_page/add_remote_dialog.blp',
    'change_version_page/change_version_page.blp',
    'snapshot_page/snapshot_page.blp',
    'snapshot_page/snapshots_list_page.blp',
    'snapshot_page/snapshot_box.blp',
    'snapshot_page/new_snapshot_dialog.blp',
    'install_page/file_install_dialog.blp',
    'install_page/install_page.blp',
    'install_page/result_row.blp',
    'install_page/select_page.blp',
    'install_page/results_page.blp',
    'install_page/pending_page.blp',
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('warehouse',
  'warehouse.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('APPID', 'io.github.flattool.Warehouse') # TODO: dynamic version and appID
if get_option('profile') == 'development'
  vcs_tag = run_command('git', 'rev-parse', '--short', 'HEAD').stdout().strip()
  conf.set('DEVEL', 'Development')
  conf.set('VERSION', meson.project_version() + '.dev-' + vcs_tag)
else
  conf.set('DEVEL', 'Default')
  conf.set('VERSION', meson.project_version())
endif
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'warehouse.py',
  output: 'warehouse',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr--r--'
)

configure_file(
  input: 'const.py',
  output: 'const.py',
  configuration: conf,
  install: true,
  install_dir: moduledir,
  install_mode: 'r-xr--r--',
)

warehouse_sources = [
  'main.py',
  'host_info.py',
  'gtk/error_toast.py',
  'gtk/sidebar_button.py',
  'gtk/loading_status.py',
  'gtk/installation_chooser.py',
  'gtk/app_row.py',
  'gtk/attempt_install_dialog.py',
  'main_window/window.py',
  'package_install_worker.py',
  'packages_page/uninstall_dialog.py',
  'packages_page/packages_page.py',
  'packages_page/filters_page.py',
  'properties_page/properties_page.py',
  'change_version_page/change_version_page.py',
  'change_version_page/change_version_worker.py',
  'user_data_page/data_box.py',
  'user_data_page/user_data_page.py',
  'user_data_page/data_subpage.py',
  'remotes_page/remotes_page.py',
  'remotes_page/remote_row.py',
  'remotes_page/add_remote_dialog.py',
  'snapshot_page/tar_worker.py',
  'snapshot_page/snapshot_page.py',
  'snapshot_page/snapshots_list_page.py',
  'snapshot_page/snapshot_box.py',
  'snapshot_page/new_snapshot_dialog.py',
  'install_page/file_install_dialog.py',
  'install_page/install_page.py',
  'install_page/result_row.py',
  'install_page/select_page.py',
  'install_page/results_page.py',
  'install_page/pending_page.py',
  'install_page/show_package.py',
  '../data/style.css',
]

install_data(warehouse_sources, install_dir: moduledir, preserve_path: true)
