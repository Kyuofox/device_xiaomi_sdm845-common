# Copyright (C) 2009 The Android Open Source Project
# Copyright (c) 2011, The Linux Foundation. All rights reserved.
# Copyright (C) 2017-2019 The LineageOS Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import common
import re
import os
from common import BlockDifference, EmptyImage, GetUserImage

# The joined list of user image partitions of source and target builds.
# - Items should be added to the list if new dynamic partitions are added.
# - Items should not be removed from the list even if dynamic partitions are
#   deleted. When generating an incremental OTA package, this script needs to
#   know that an image is present in source build but not in target build.
USERIMAGE_PARTITIONS = [
    "odm",
    "product",
    "system_ext",
]

def GetUserImages(input_tmp, input_zip):
  return {partition: GetUserImage(partition, input_tmp, input_zip)
          for partition in USERIMAGE_PARTITIONS
          if os.path.exists(os.path.join(input_tmp,
                                         "IMAGES", partition + ".img"))}

def FullOTA_GetBlockDifferences(info):
  images = GetUserImages(info.input_tmp, info.input_zip)
  return [BlockDifference(partition, image)
          for partition, image in images.items()]

def IncrementalOTA_GetBlockDifferences(info):
  source_images = GetUserImages(info.source_tmp, info.source_zip)
  target_images = GetUserImages(info.target_tmp, info.target_zip)

  # Use EmptyImage() as a placeholder for partitions that will be deleted.
  for partition in source_images:
    target_images.setdefault(partition, EmptyImage())

  # Use source_images.get() because new partitions are not in source_images.
  return [BlockDifference(partition, target_image, source_images.get(partition))
          for partition, target_image in target_images.items()]

def FullOTA_InstallEnd(info):
  input_zip = info.input_zip
  OTA_UpdateFirmware(info)
  OTA_InstallEnd(info, input_zip)
  return

def IncrementalOTA_InstallEnd(info):
  input_zip = info.target_zip
  OTA_UpdateFirmware(info)
  OTA_InstallEnd(info, input_zip)
  return

def OTA_UpdateFirmware(info):
  info.script.AppendExtra('ui_print("Flashing firmware images");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/abl.elf", "/dev/block/bootdevice/by-name/abl_a");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/abl.elf", "/dev/block/bootdevice/by-name/abl_b");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/cmnlib64.img", "/dev/block/bootdevice/by-name/cmnlib64_a");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/aop.img", "/dev/block/bootdevice/by-name/aop_a");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/devcfg.img", "/dev/block/bootdevice/by-name/devcfg_a");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/qupfw.img", "/dev/block/bootdevice/by-name/qupfw_a");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/tz.img", "/dev/block/bootdevice/by-name/tz_a");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/storsec.img", "/dev/block/bootdevice/by-name/storsec_a");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/keymaster.img", "/dev/block/bootdevice/by-name/keymaster_a");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/bluetooth.img", "/dev/block/bootdevice/by-name/bluetooth");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/xbl.img", "/dev/block/bootdevice/by-name/xbl_a");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/modem.img", "/dev/block/bootdevice/by-name/modem");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/xbl_config.img", "/dev/block/bootdevice/by-name/xbl_config_a");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/dsp.img", "/dev/block/bootdevice/by-name/dsp");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/logo.img", "/dev/block/bootdevice/by-name/logo");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/cmnlib.img", "/dev/block/bootdevice/by-name/cmnlib_a");')
  info.script.AppendExtra('package_extract_file("install/firmware-update/hyp.img", "/dev/block/bootdevice/by-name/hyp_a");')

def AddImage(info, dir, input_zip, basename, dest):
  path = dir + "/" + basename
  if path not in input_zip.namelist():
    return

  data = input_zip.read(path)
  common.ZipWriteStr(info.output_zip, basename, data)
  info.script.Print("Patching {} image unconditionally...".format(dest.split('/')[-1]))
  info.script.AppendExtra('package_extract_file("%s", "%s");' % (basename, dest))

def FullOTA_InstallBegin(info):
  AddImage(info, "RADIO", "super_dummy.img", "/tmp/super_dummy.img");
  info.script.AppendExtra('package_extract_file("install/bin/flash_super_dummy.sh", "/tmp/flash_super_dummy.sh");')
  info.script.AppendExtra('set_metadata("/tmp/flash_super_dummy.sh", "uid", 0, "gid", 0, "mode", 0755);')
  info.script.AppendExtra('run_program("/tmp/flash_super_dummy.sh");')
  return

def OTA_InstallEnd(info, input_zip):
  AddImage(info, input_zip, "IMAGES", "dtbo.img", "/dev/block/bootdevice/by-name/dtbo")
  AddImage(info, input_zip, "IMAGES", "vbmeta.img", "/dev/block/bootdevice/by-name/vbmeta")
  return
