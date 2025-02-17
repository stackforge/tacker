# Copyright (C) 2021 Nippon Telegraph and Telephone Corporation
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


from oslo_log import log as logging

from tacker.sol_refactored.api.schemas import common_types
from tacker.sol_refactored.api import validator
from tacker.sol_refactored.common import exceptions as sol_ex
from tacker.sol_refactored import objects


LOG = logging.getLogger(__name__)  # not used at the moment


def get_inst(context, inst_id):
    inst = objects.VnfInstanceV2.get_by_id(context, inst_id)
    if inst is None:
        raise sol_ex.VnfInstanceNotFound(inst_id=inst_id)
    return inst


def get_inst_all(context, marker=None):
    return objects.VnfInstanceV2.get_all(context, marker)


def inst_href(inst_id, endpoint):
    return "{}/vnflcm/v2/vnf_instances/{}".format(endpoint, inst_id)


def make_inst_links(inst, endpoint):
    self_href = inst_href(inst['id'], endpoint)
    links = {'self': {'href': self_href}}
    if inst['instantiationState'] == 'NOT_INSTANTIATED':
        links['instantiate'] = {'href': self_href + "/instantiate"}
    else:  # 'INSTANTIATED'
        links['terminate'] = {'href': self_href + "/terminate"}
        links['scale'] = {'href': self_href + "/scale"}
        links['heal'] = {'href': self_href + "/heal"}
        links['changeExtConn'] = {'href': self_href + "/change_ext_conn"}
        # NOTE: add when the operation supported

    return links


# see IETF RFC 7396
def json_merge_patch(target, patch):
    if isinstance(patch, dict):
        if not isinstance(target, dict):
            target = {}
        for key, value in patch.items():
            if value is None:
                if key in target:
                    del target[key]
            else:
                target[key] = json_merge_patch(target.get(key), value)
        return target
    else:
        return patch


def select_vim_info(vim_connection_info, return_key=False):
    # NOTE: It is assumed that vimConnectionInfo has only one item
    # at the moment. If there are multiple items, it is uncertain
    # which item is selected.
    for key, value in vim_connection_info.items():
        if value.vimType == 'kubernetes':
            value.vimType = 'ETSINFV.KUBERNETES.V_1'
        if return_key:
            return key, value
        return value


def check_metadata_format(metadata):
    """Check VnfInstance.metadata format"""
    # NOTE: This method checks keys which Tacker supports originally.
    # The key supporting is only 'VDU_VNFc_mapping' for the moment.

    _vdu_vnfc_mapping = {
        'type': 'object',
        'patternProperties': {
            '^.*$': {
                'type': 'array',
                'items': common_types.IdentifierInVnf
            }
        }
    }

    if 'VDU_VNFc_mapping' in metadata:
        schema_validator = validator.SolSchemaValidator(_vdu_vnfc_mapping)
        schema_validator.validate(metadata['VDU_VNFc_mapping'])

        all_vnfc_info_ids = list()
        for vnfc_info_ids in metadata['VDU_VNFc_mapping'].values():
            all_vnfc_info_ids.extend(vnfc_info_ids)

        if len(all_vnfc_info_ids) > len(set(all_vnfc_info_ids)):
            raise sol_ex.SolValidationError(
                detail="Duplicated vnfcInfo ids found in "
                "metadata['VDU_VNFc_mapping'].")


def _get_current_scale_level(inst, aspect_id):
    if (inst.obj_attr_is_set('instantiatedVnfInfo') and
            inst.instantiatedVnfInfo.obj_attr_is_set('scaleStatus')):
        for scale_info in inst.instantiatedVnfInfo.scaleStatus:
            if scale_info.aspectId == aspect_id:
                return scale_info.scaleLevel


def _get_max_scale_level(inst, aspect_id):
    if (inst.obj_attr_is_set('instantiatedVnfInfo') and
            inst.instantiatedVnfInfo.obj_attr_is_set('maxScaleLevels')):
        for scale_info in inst.instantiatedVnfInfo.maxScaleLevels:
            if scale_info.aspectId == aspect_id:
                return scale_info.scaleLevel


def check_scale_level(inst, aspect_id, scale_type, num_steps):
    orig_num_steps = num_steps

    scale_level = _get_current_scale_level(inst, aspect_id)
    max_scale_level = _get_max_scale_level(inst, aspect_id)
    if scale_level is None or max_scale_level is None:
        raise sol_ex.InvalidScaleAspectId(aspect_id=aspect_id)

    if scale_type == 'SCALE_IN':
        num_steps *= -1
    scale_level += num_steps
    if scale_level < 0 or scale_level > max_scale_level:
        raise sol_ex.InvalidScaleNumberOfSteps(
            num_steps=orig_num_steps)


def check_vnfc_ids(inst, vnfc_ids):
    inst_vnfc_ids = []
    if (inst.obj_attr_is_set('instantiatedVnfInfo') and
            inst.instantiatedVnfInfo.obj_attr_is_set('vnfcInfo')):
        inst_vnfc_ids = [vnfc.id for vnfc in inst.instantiatedVnfInfo.vnfcInfo]

    for req_vnfc_id in vnfc_ids:
        if req_vnfc_id not in inst_vnfc_ids:
            raise sol_ex.SolValidationError(
                detail="vnfcInstanceId(%s) does not exist." % req_vnfc_id)
