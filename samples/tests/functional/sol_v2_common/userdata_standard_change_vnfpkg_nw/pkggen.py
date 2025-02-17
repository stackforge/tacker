# Copyright (C) 2022 Nippon Telegraph and Telephone Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import os
import shutil
import tempfile

from oslo_utils import uuidutils

from tacker.tests.functional.sol_v2_common import paramgen
from tacker.tests.functional.sol_v2_common import utils as common_utils
from tacker.tests import utils


zip_file_name = os.path.basename(os.path.abspath(".")) + '.zip'
tmp_dir = tempfile.mkdtemp()
vnfd_id = uuidutils.generate_uuid()

image_path = utils.test_etc_sample("etsi/nfv/common/Files/images",
    "cirros-0.5.2-x86_64-disk.img")

# tacker/sol_refactored/infra_drivers/openstack/userdata_standard.py
userdata_path = utils.userdata("userdata_standard.py")

common_utils.make_zip(".", tmp_dir, vnfd_id, image_path=image_path,
    userdata_path=userdata_path)

shutil.copy(os.path.join(tmp_dir, zip_file_name), ".")
shutil.rmtree(tmp_dir)

net_ids = common_utils.get_network_ids(['net0', 'net1', 'net_mgmt'])
subnet_ids = common_utils.get_subnet_ids(['subnet0', 'subnet1'])

change_vnfpkg_req = paramgen.sample5_change_vnfpkg(
    vnfd_id, net_ids, subnet_ids)
change_vnfpkg_back_req = paramgen.sample5_change_vnfpkg_back(
    "input-original-vnfd-id", net_ids, subnet_ids)

with open("change_vnfpkg_req", "w") as f:
    f.write(json.dumps(change_vnfpkg_req, indent=2))
with open("change_vnfpkg_back_req", "w") as f:
    f.write(json.dumps(change_vnfpkg_back_req, indent=2))
