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
import shutil

from tacker.tests.functional.sol_kubernetes_v2 import paramgen
from tacker.tests.functional.sol_kubernetes_v2 import zipgen


vnfd_id, zip_path = zipgen.test_helm_instantiate()

shutil.move(zip_path, ".")
shutil.rmtree(zip_path.rsplit('/', 1)[0])

create_req = paramgen.test_helm_instantiate_create(vnfd_id)

# if you instantiate with all k8s resource
# please change auth_url, bearer_token and ssl_ca_cert
# to your own k8s cluster's info
auth_url = "https://127.0.0.1:6443"
bearer_token = "your_k8s_cluster_bearer_token"
ssl_ca_cert = "k8s_ssl_ca_cert"
helm_instantiate_req = paramgen.helm_instantiate(
    auth_url, bearer_token, ssl_ca_cert)

helm_terminate_req = paramgen.helm_terminate()
helm_scale_out = paramgen.helm_scale_out()
helm_scale_in = paramgen.helm_scale_in()
helm_heal = paramgen.helm_heal(["replace real vnfc ids"])

with open("create_req", "w", encoding='utf-8') as f:
    f.write(json.dumps(create_req, indent=2))

with open("helm_instantiate_req", "w", encoding='utf-8') as f:
    f.write(json.dumps(helm_instantiate_req, indent=2))

with open("helm_terminate_req", "w", encoding='utf-8') as f:
    f.write(json.dumps(helm_terminate_req, indent=2))

with open("helm_scale_out", "w", encoding='utf-8') as f:
    f.write(json.dumps(helm_scale_out, indent=2))

with open("helm_scale_in", "w", encoding='utf-8') as f:
    f.write(json.dumps(helm_scale_in, indent=2))

with open("helm_heal", "w", encoding='utf-8') as f:
    f.write(json.dumps(helm_heal, indent=2))
