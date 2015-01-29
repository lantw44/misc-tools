#!/usr/bin/env python2

import yum
from gi.repository import Gtk


class YumDB:
	def __init__(self):
		self.yb = yum.YumBase()
		self.yb.conf

	def get_reasons(self, patterns=None):
		reasons = []
		for pkg in sorted(self.yb.rpmdb.returnPackages(patterns=patterns)):
			reasons.append({'nevra': pkg.nevra, \
				'group_member': pkg.yumdb_info.group_member \
				if hasattr(pkg.yumdb_info, 'group_member') else '', \
				'reason': pkg.yumdb_info.reason \
				if hasattr(pkg.yumdb_info, 'reason') else '<unset>', \
				'reason_editor': pkg.yumdb_info.reason_editor \
				if hasattr(pkg.yumdb_info, 'reason_editor') else ''})
		return reasons

	def get_summary(self, nevra):
		return self.yb.rpmdb.returnPackages(patterns=[ nevra ])[0].summary

	def get_description(self, nevra):
		return self.yb.rpmdb.returnPackages(patterns=[ nevra ])[0].description

	def set_reason(self, nevra, value):
		try:
			pkg = self.yb.rpmdb.returnPackages(patterns=[ nevra ])[0]
		except IndexError as e:
			return '{} does not exists!'.format(nevra)

		try:
			pkg.yumdb_info.reason = value
			pkg.yumdb_info.reason_editor = 'modified'
		except Exception as e:
			return '{} fails: {}'.format(nevra, e[1])

		return True


class PkgList(Gtk.TreeView):
	def add_column(self, name, index):
		renderer = Gtk.CellRendererText()
		column = Gtk.TreeViewColumn(name)
		column.pack_start(renderer, True)
		column.add_attribute(renderer, 'text', index)
		column.set_resizable(True)
		column.set_sort_column_id(index)
		column.set_sort_indicator(index)
		self.append_column(column)

class ReasonEditor(Gtk.Window):
	COLUMN_NUMBER = 0
	COLUMN_NEVRA = 1
	COLUMN_GROUP = 2
	COLUMN_REASON = 3
	COLUMN_STATUS = 4

	def __init__(self):
		Gtk.Window.__init__(self, title='YumDB Reason Editor')
		self.set_default_size(800, 600)

		self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

		self.pkg_store = Gtk.ListStore(int, str, str, str, str)
		self.pkg_list = PkgList(self.pkg_store)
		self.pkg_list.add_column('#', 0)
		self.pkg_list.add_column('Name-Version-Arch', 1)
		self.pkg_list.add_column('Group', 2)
		self.pkg_list.add_column('Reason', 3)
		self.pkg_list.add_column('Status', 4)
		self.pkg_list.set_enable_search(False)
		self.pkg_list.set_search_column(self.COLUMN_NEVRA)
		self.pkg_list.connect('row-activated', self.toggle_reason)

		self.pkg_scrollable = Gtk.ScrolledWindow()
		self.pkg_scrollable.add(self.pkg_list)

		self.count_label = Gtk.Label()

		self.bottom_buttons = Gtk.Box()
		self.reload_db = Gtk.Button.new_with_mnemonic(label='_Reload YumDB')
		self.reload_db.connect('clicked', self.load_database)
		self.show_info = Gtk.Button.new_with_mnemonic(label='_Info')
		self.show_info.connect('clicked', self.show_summary_description)
		self.enable_search = Gtk.ToggleButton('_Search Disabled')
		self.enable_search.connect('toggled', self.toggle_search)
		self.enable_search.set_use_underline(True)
		self.bottom_buttons.pack_start(self.reload_db, True, True, 0)
		self.bottom_buttons.pack_start(self.show_info, True, True, 0)
		self.bottom_buttons.pack_start(self.enable_search, True, True, 0)

		self.vbox.pack_start(self.pkg_scrollable, True, True, 0)
		self.vbox.pack_start(self.count_label, False, False, 0)
		self.vbox.pack_start(self.bottom_buttons, False, False, 0)
		self.add(self.vbox)
		self.show_all()

		self.load_database()

	def load_database(self, unused=None):
		self.yumdb = YumDB()
		self.pkg_store.clear()

		print('Loading database ...')
		data = self.yumdb.get_reasons()

		print('Adding entries ...')
		self.dep_count = 0
		self.user_count = 0
		for index, entry in enumerate(data):
			self.pkg_store.append([	index + 1,
				entry['nevra'], entry['group_member'],
				entry['reason'], entry['reason_editor'] ])
			if entry['reason'] == 'dep':
				self.dep_count += 1
			else:
				self.user_count += 1

		self.pkg_count = index + 1
		self.update_count()
		self.show_all()

	def update_count(self):
		self.count_label.set_label('{} dep, {} user, {} pkgs'.format(
			self.dep_count, self.user_count, self.pkg_count))

	def toggle_search(self, unused=None):
		if self.enable_search.get_active():
			self.enable_search.set_label('_Search Enabled')
			self.pkg_list.set_enable_search(True)
		else:
			self.enable_search.set_label('_Search Disabled')
			self.pkg_list.set_enable_search(False)

	def toggle_reason(self, path, column, unused=None):
		model = self.pkg_list.get_model()
		tree_path = self.pkg_list.get_cursor()[0]
		if tree_path == None:
			return

		tree_iter = model.get_iter(tree_path)
		if tree_iter == None:
			return

		nevra = model[tree_iter][self.COLUMN_NEVRA]
		is_dep = model[tree_iter][self.COLUMN_REASON] == 'dep'

		result = self.yumdb.set_reason(nevra, 'user' if is_dep else 'dep')
		if result != True:
			error_dialog = Gtk.MessageDialog(
				title='YumDB Error',
				buttons=Gtk.ButtonsType.CLOSE,
				message_type=Gtk.MessageType.ERROR,
				message_format=result)
			error_dialog.run()
			error_dialog.destroy()
			return

		new_entry = self.yumdb.get_reasons([ nevra ])[0]
		model[tree_iter][self.COLUMN_REASON] = new_entry['reason']
		model[tree_iter][self.COLUMN_STATUS] = new_entry['reason_editor']
		tree_path.next()
		self.pkg_list.set_cursor(tree_path)
		if is_dep:
			self.dep_count -= 1
			self.user_count += 1
		else:
			self.dep_count += 1
			self.user_count -= 1
		self.update_count()

	def show_summary_description(self, unused=None):
		model, tree_iter = self.pkg_list.get_selection().get_selected()
		if tree_iter == None:
			return
		nevra = model[tree_iter][1]

		dialog = Gtk.MessageDialog(
			title=nevra,
			buttons=Gtk.ButtonsType.CLOSE,
			message_type=Gtk.MessageType.INFO,
			message_format=None)
		dialog.set_markup('<big><b>{}</b></big>\n\n{}'.format(
			self.yumdb.get_summary(nevra),
			self.yumdb.get_description(nevra)))
		dialog.run()
		dialog.destroy()


if __name__ == '__main__':
	editor = ReasonEditor()
	editor.connect('delete-event', Gtk.main_quit)
	Gtk.main()
