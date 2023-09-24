"""
This file is used to extract the current system running status, such as CPU and memory.
Please pay attention! The extraction parameters included are:
uptime: Extract the current system running status.
kernel_info: Extract the kernel parameter information of the current system.
cpuinfo: Extract the cpu usage information of the current system.
avg_use_cpu: Calculate the average cpu usage of the current system.
memory_static_info: Extract the memory status information of the current system.
memory_info: Extract the memory operation information of the current system.
"""

import os
import re
import yaml
import psutil


class loads():

    def uptime(self):

        """-----------------------------------
        The information begins to be extracted
        -----------------------------------"""

        uptime_info \
            = re.sub(
            r"\n",
            "",
            os.popen(
                "%suptime"
                % (self.bin_path)
            ).read()
        )

        return {

            "uptime_info":
                uptime_info

        }

    def kernel_info(self):

        """-----------------------------------
        The information begins to be extracted
        -----------------------------------"""

        kernel_info \
            = re.sub(
            r"\n|#",
            "",
            os.popen(
                "%suname -a"
                % (self.bin_path)
            )
            .read()
        )

        return \
            {

                "kernel":
                    kernel_info

            }

    def __init__(self):

        self.bin_path \
            = '/usr/bin/'

    def cpuinfo(self):

        num = 0

        cpu_time = 0

        state_name = ['user',
                      'nice',
                      'system',
                      'idle',
                      'iowait',
                      'irq',
                      'softirq',
                      'steal',
                      'guest',
                      'guest_nice']

        time_info = {}

        """-----------------------------------
        The information begins to be extracted
        -----------------------------------"""

        for i in \
                psutil.cpu_times():

            time_info[state_name[num]] \
                = "{}".format(i)

            num += 1

            cpu_time += i

        cpu_time \
            = str(cpu_time/60)

        """-----------------------------
        Start organizing the information
        -----------------------------"""

        cpu_info \
            = {"cpu_KernelNumber":
                   os.cpu_count(),

                    "sum_minute":
                        "{}{}"
                        .format(
                            cpu_time[0:cpu_time
                                       .find(".",
                                             0,
                                             len(cpu_time)
                                             )+3
                            ],
                            "Minute")
               }

        cpu_info\
            .update(time_info)

        return \
            cpu_info

    def avg_use_cpu(self):

        """-----------------------------------
        The information begins to be extracted
        -----------------------------------"""

        cpustat_info \
            = os.popen(
            "%smpstat"
            % (self.bin_path)
        )\
            .read()

        num \
            = 0

        avgcpu_info \
            = {}

        avgcpu_header \
            = []

        """-----------------------------
        Start organizing the information
        -----------------------------"""

        for header in \
                cpustat_info.split(
                    "\n"
                )[1 << 1]\
                        .split(" "):

            if header \
                    != "":

                avgcpu_header\
                    .append(header)

        cpustat_time \
            = avgcpu_header.pop(0)

        for info in \
                cpustat_info.split(
                    "\n"
                )[(1 << 1)+1]\
                        .split(" "):

            if info \
                    != "":

                if info \
                        != cpustat_time:

                    avgcpu_info\
                        .update(
                        {
                            avgcpu_header[num]:
                                info
                        }
                    )
                    num \
                        += 1
        avgcpu_info['CPU'] \
            = os.popen(
            "%smpstat \
            | %sgrep '_' \
            | %sawk '{print $6,$7}'"
                                      %(self.bin_path,
                                        self.bin_path,
                                        self.bin_path))\
            .read()\
            .replace("\n",
                     "")
        return avgcpu_info

    def memory_static_info(self):

        dict_memory \
            = {}

        """-----------------------------------
        The information begins to be extracted
        -----------------------------------"""

        for mem in \
                os.popen(
                    "%scat /proc/meminfo"
                    % (self.bin_path)
                ).read()\
                        .split("\n"):

            memory \
                = yaml.load(mem,
                            Loader
                            =yaml.FullLoader)

            if "dict" in \
                    str(type(memory)):

                dict_memory\
                    .update(
                    {x: memory[x] for x in memory})

        return dict_memory

    def memory_info(self):

        column_name = ["total",
                       "available",
                       "percent",
                       "used",
                       "free",
                       "active",
                       "inactive",
                       "buffers",
                       "cached",
                       "shared",
                       "slab",
                       "sin",
                       "sout"]

        swap_sequence = [0,
                         3,
                         4,
                         2,
                         11,
                         12]

        num \
            = 0

        dict_memory \
            = {}

        dict_swap \
            = {}

        """-----------------------------------
        The information begins to be extracted
        -----------------------------------"""

        for memory in \
                psutil\
                        .virtual_memory():

            dict_memory[column_name[num]] \
                = "{}".format(memory)

            num \
                += 1

        for swap in \
                range(len(swap_sequence)):

            dict_swap[column_name[swap]] \
                = "{}".format(
                psutil
                .swap_memory()[swap]
            )

        return {

            "memory":
                dict_memory,

            "swap":
                dict_swap

        }


if __name__ != "__main__":
    loads