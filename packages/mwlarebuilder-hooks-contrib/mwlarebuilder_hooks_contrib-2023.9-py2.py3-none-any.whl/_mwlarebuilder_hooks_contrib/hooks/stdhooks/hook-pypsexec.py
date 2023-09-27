# ------------------------------------------------------------------
# Copyright (c) 2022 MwlareBuilder Development Team.
#
# This file is distributed under the terms of the GNU General Public
# License (version 2.0 or later).
#
# The full license is available in LICENSE.GPL.txt, distributed with
# this software.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# ------------------------------------------------------------------

# The bundled paexec.exe file needs to be collected (as data file; on any platform)
# because it is deployed to the remote side during execution.

from MwlareBuilder.utils.hooks import collect_data_files

datas = collect_data_files('pypsexec')
