# -----------------------------------------------------------------------------
# Copyright (c) 2013-2018, MwlareBuilder Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
# -----------------------------------------------------------------------------

# Hook for Parso, a static analysis tool https://pypi.org/project/jedi/ (IPython dependency)

from MwlareBuilder.utils.hooks import collect_data_files

datas = collect_data_files('parso')
