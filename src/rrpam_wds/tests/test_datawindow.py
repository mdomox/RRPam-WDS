from rrpam_wds.gui import set_pyqt_api  # isort:skip # NOQA
import logging
import os
import shutil
import tempfile
from uuid import uuid4

import mock
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QDialog

import rrpam_wds.constants as c
from rrpam_wds.tests.test_utils import Test_Parent
from rrpam_wds.tests.test_utils import main
from rrpam_wds.tests.test_utils import set_text_spinbox
from rrpam_wds.tests.test_utils import set_text_textbox


def uniquestring():
    return str(uuid4())


class TC(Test_Parent):
    logger = logging.getLogger()

    def test_set_information_sets_the_right_data(self):
        results = (
            '2', [['.2', '.5', '500.0'], ['1.2e-4', '5e-1', '125.'], ['1', '2', '.1'], ['4', '5', '999.']])
        self.aw.datawindow.set_information(results)
        self.assertEqual(self.aw.datawindow.ui.no_groups.text(), '2')
        self.assertEqual(self.aw.datawindow.assetgrouplist[1].A.text(), '1.2e-4')
        # self.assertEqual(self.aw.datawindow.assetgrouplist[3].age.text(), '6')

    def test_get_information_returns_the_right_data(self):
        # create some groups
        item = self.aw.datawindow.ui.no_groups
        set_text_spinbox(item, 12)
        A1 = 1.12e-4
        N01 = 1.34e-5
        cost1 = 22.
        A2 = 1.2e-4
        N02 = 2.2e-1
        one = self.aw.datawindow.assetgrouplist[11]
        set_text_textbox(one.A, A1)
        A1 = float(one.A.text())
        set_text_textbox(one.N0, N01)
        N01 = float(one.N0.text())
        set_text_textbox(one.cost, cost1)
        cost1 = float(one.cost.text())
        box = self.aw.datawindow.assetgrouplist[2]
        set_text_textbox(box.A, A2)
        A2 = float(box.A.text())
        set_text_textbox(box.N0, N02)
        N02 = float(box.N0.text())
        set_text_spinbox(item, 4)
        QTest.keyPress(item, Qt.Key_Return)  # now we have only 4 active items
        active, values = self.aw.datawindow.get_information(all=True)
        self.assertEqual(active, 4)
        self.assertEqual(values[11][0], A1)
        self.assertEqual(values[11][1], N01)
        self.assertEqual(values[11][2], cost1)
        self.assertEqual(values[2][0], A2)
        self.assertEqual(values[2][1], N02)

    def test_saveing_and_loading_asset_groups_works_properly(self):
        pp = self.aw.projectgui.projectproperties.dataset
        with mock.patch.object(pp, "_write_network_data", autospec=True) as mock_write_network_data:
            with mock.patch.object(pp, "_read_network_data", autospec=True) as mock__read_network_data:
                mock_write_network_data.return_value = True
                mock__read_network_data.return_value = True
                ddir = os.path.join(tempfile.gettempdir(), "__xxx_rramwds_test")
                prjfile = os.path.join(ddir, "__xxx__rrpamwds_test_assetgroups")
                shutil.rmtree(ddir, ignore_errors=True)
                os.mkdir(ddir)
                os.mkdir(c._get_dir_and_extention(prjfile)[1])
                self.assertFalse(os.path.isfile(pp.get_assetgroups_file(prjfile)))
                self.aw.datawindow.ui.no_groups.setValue(10)
                pp.group_list_to_save_or_load = self.aw.datawindow.get_information(all=True)
                pp._write_assetgroup_data(prjfile)
                self.assertTrue(os.path.isfile(pp.get_assetgroups_file(prjfile)))
                self.aw.datawindow._set_no_groups(1)
                pp._read_asset_group_data(prjfile)
                self.aw.datawindow.set_information(pp.group_list_to_save_or_load)
                self.assertEqual(self.aw.datawindow.activenumberofgroups, 10)

    def test_datawindow_is_derived_from_QDialog(self):
        """Needed for it to use pyqt5 signal slot connections"""
        dw = self.aw.datawindow
        self.assertIsInstance(dw, QDialog)

    def test_group_properties_can_not_have_empty_values(self):
        A = self.aw.datawindow.assetgrouplist[0].A
        N0 = self.aw.datawindow.assetgrouplist[0].N0
        cost = self.aw.datawindow.assetgrouplist[0].cost
        # age = A = self.aw.datawindow.assetgrouplist[0].age
        set_text_textbox(A, "", enter=True)
        set_text_textbox(N0, "", enter=True)
        set_text_textbox(cost, "", enter=True)

        # set_text_spinbox(age, "")
        float(A.text())
        float(N0.text())
        float(cost.text())
        self.assertTrue(True)

    def test_when_attempted_to_close_datawindow_will_be_minized(self):
        dw = self.aw.datawindow
        t = uniquestring()
        dw.setWindowTitle(t)
        self.assertFalse(dw.isMinimized())
        dw.close()
        self.assertEqual(
            len([x for x in self.aw.mdi.subWindowList() if x.widget() .windowTitle() == t]),
            1)
        self.assertTrue(dw.isMinimized())

    def test_presseing_esc_does_not_close_or_clear_the_data_window(self):
        dw = self.aw.datawindow
        self.aw.show()
        self.assertTrue(dw.isVisible())
        QTest.keyPress(dw, Qt.Key_Escape)
        self.assertTrue(dw.isVisible())
        self.aw.hide()

    def test_number_of_property_groups_is_kept_equal_to_no_groups_spinbox(self):
        self.compare()
        item = self.aw.datawindow.ui.no_groups
        set_text_spinbox(item, "12")
        self.compare()
        set_text_spinbox(item, "2")
        self.compare()
        set_text_spinbox(item, "8")
        QTest.keyPress(item, Qt.Key_Return)
        self.compare()
        set_text_spinbox(item, "-5")
        self.compare()

    def compare(self):
        n = len(self.aw.datawindow.get_active_groups())
        self.logger.info("n=%d" % n)
        self.assertEqual(n, self.aw.datawindow.ui.no_groups.value())
        self.assertEqual(n, self.aw.datawindow.activenumberofgroups)

    def test_A_No_year_parameters_can_not_be_set_to_invalid_values(self):
        A = self.aw.datawindow.assetgrouplist[0].A
        N0 = self.aw.datawindow.assetgrouplist[0].N0
        # age = self.aw.datawindow.assetgrouplist[0].age
        set_text_textbox(A, "1.ek58")
        set_text_textbox(N0, "ab")
        # set_text_spinbox(age, "28.8")
        float(A.text())
        float(N0.text())
        # int(age.text())
        self.assertTrue(True)


if __name__ == '__main__':  # pragma: no cover
    main(TC, test=False)
