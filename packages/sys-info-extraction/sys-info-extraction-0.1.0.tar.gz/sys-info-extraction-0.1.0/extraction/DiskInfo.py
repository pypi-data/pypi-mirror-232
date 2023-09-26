"""
This file is used to extract the disk usage and system storage mounting information under the current system,
please pay attention! The extraction parameters included are:
disk_all_info: Extract all disk sectors in the current system.
disk_use: Extract the disk usage of the current system.
mount_info: Extract the local mounting status of the current system.
volume_group_info: Extract the VG volume group status of the current system.
logical_group_info: Extract the logical volume group status of the current system.
"""
import os
import re
import psutil


class diskinfo():
    """
    Disk sector partitioning
    """
    def disk_all_info(self):

        try:

            Disk_allinfo \
                = {}

            num \
                = 0

            """-----------------------------------
            The information begins to be extracted
            -----------------------------------"""

            for disk_all in \
                    os.popen(
                        "%sfdisk -l \
                        | grep Disk \
                        | grep '/'"
                             %(self.sbin_path)
                             ).read().\
                            split("\n"):

                """---------------------
                Perform judgment actions
                ---------------------"""

                num \
                    += 1

                if disk_all != "":

                    Disk_allinfo[num] \
                        = disk_all

                    """-----------------------
                    Make exception definitions
                    -----------------------"""

        except Exception \
                as err:

            Disk_allinfo['error_info'] \
                = [str(err)]

        return {

            "check_name":

                "disk_all",

            "check_result":

                Disk_allinfo

        }

    """
    Disk usage
    """

    def disk_use(self):
        try:
            dict_disk \
                = {}

            """-----------------------------------
            The information begins to be extracted
            -----------------------------------"""

            psutil_diskinfo = psutil.\
                disk_partitions()

            """-----------------
            Start data wrangling
            -----------------"""

            for info in psutil_diskinfo:

                column_header = ['total',
                                 'used',
                                 'free',
                                 'percent']

                dict_column = {}

                """---------------------------------------
                Start organizing and summarizing your data
                ---------------------------------------"""

                for num in range(4):

                    dict_column[column_header[num]] \
                        = "{}".format(
                        psutil.
                        disk_usage(
                            info[1]
                        )[num]
                    )

                dict_disk[info[1]] \
                    = dict_column

                """-----------------------
                Make exception definitions
                -----------------------"""

        except Exception as e:

            dict_disk["error_info"] \
                = [str(e)]

        return {
            "check_name":
                'check_disk',
            "check_result":
                dict_disk
        }

    def __init__(self):
        self.bin_path \
            = '/usr/bin/'
        self.sbin_path \
            = '/usr/sbin/'

    """---------------------------------
    Extract the system mount information
    ---------------------------------"""

    def mount_info(self):

        try:

            mount_info \
                = {}

            num \
                = 0

            """-----------------
            Start data wrangling
            -----------------"""

            read_mount_info \
                = os.popen(
                "%smount"
                %(
                    self.bin_path
                )
            ).read()

            """-------------------------------
            Organize the extracted information
            -------------------------------"""

            for i in \
                    read_mount_info.\
                            split("\n"):

                num += 1

                """--------------------------
                Execution judgment conditions
                --------------------------"""

                if i != "":

                    info \
                        = re.\
                        sub(
                        r"\(.+\)",
                        "",
                        i)

                    mount_info['mount_info{}'
                    .format(num)] = \
                        info.replace("on",
                                     "->").\
                            replace(" type ",
                                    " type:")

                    """-----------------------
                    Make exception definitions
                    -----------------------"""

        except Exception \
                as err:
            mount_info['error_info'] \
                = [str(err)]

        return {

            "check_name":
                "mount_info",

            "check_result":
                mount_info

        }

    """----------------------------------------
    Extract the system volume group information
    ----------------------------------------"""

    def volume_group_info(self):

        try:

            dict_volumegroup \
                = {}

            """-----------------
            Start data wrangling
            -----------------"""

            vgdisplay \
                = os.\
                popen(
                "%svgdisplay \
                | grep VG"
                %(self.sbin_path)
            ).\
                read()

            """-----------------------
            Start organizing your data
            -----------------------"""

            for vg_info in\
                    vgdisplay.\
                            split("\n"):

                if vg_info\
                        !="":

                    info \
                        = vg_info\
                        .replace(
                        "  ",
                        "")\
                        .split(" ")
                    dict_volumegroup[info[1]] \
                        = "{}"\
                        .format(
                        ""
                        .join(
                            info[
                            2:
                            2<<1
                            ]
                        )
                    )

                    """-----------------------
                    Make exception definitions
                    -----------------------"""

        except Exception \
                as err:
            dict_volumegroup['error_info'] \
                = [str(err)]

        return {

            "check_name":
                'volume_group',

            "check_result":
                dict_volumegroup

        }

    """-----------------------------------------
    Begins extracting logical volume information
    -----------------------------------------"""

    def logical_group_info(self):

        try:

            volume_name \
                = "LogicalVolume"

            volume_sequence \
                = 0
            logical_volume_data \
                = []

            """-----------------
            Start data wrangling
            -----------------"""

            lv_info \
                = os\
                .popen(
                "%slvdisplay"
                %(self.sbin_path)
            )\
                .read()

            """-------------------------------
            Organize the extracted information
            -------------------------------"""

            for info in \
                    lv_info\
                            .split("\n"):

                if info \
                        != "":

                    if "Logical" in\
                            info:

                        volume_sequence \
                            += 1

                    else:

                        lvdisplay_info \
                            = re.sub(
                            r"^:'",
                            "",
                            re.sub(
                                r"  +",
                                ":'",
                                info
                            )
                        )
                        lvdisplay_info \
                            = lvdisplay_info\
                            .split(":'")

                        if lvdisplay_info[0] \
                                != "":

                            logical_volume_data\
                                .append(
                                {volume_name +
                                 '{}'
                                 .format(
                                     volume_sequence
                                 ):
                                     {lvdisplay_info[0]:
                                          ''
                                          .join(
                                              lvdisplay_info[1:3]
                                          )
                                     }
                                }
                            )

                            """-----------------------
                            Make exception definitions
                            -----------------------"""

        except Exception \
                as err:
            logical_volume_data["error_info"] \
                = [str(err)]

        return {

            "check_name":
                'logical_group',

            "check_result":
                logical_volume_data

        }


if __name__ != "__main__":
    diskinfo