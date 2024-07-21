# Copyright 2016-2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Amazon Software License (the "License"). You may not use
# this file except in compliance with the License. A copy of the License is
# located at
#
#  http://aws.amazon.com/asl/
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express
# or implied. See the License for the specific language governing
# permissions and limitations under the License.

from awsglue.transforms import GlueTransform
from awsglue.utils import _global_args

class Relationalize(GlueTransform):
    """
    Relationalizes a dynamic frame. i.e. produces a list of frames that are
    generated by unnesting nested columns and pivoting array columns. The
    pivoted array column can be joined to the root table using the joinkey
    generated in unnest phase
    :param frame: DynamicFrame to relationalize
    :param staging_path: path to store partitions of pivoted tables in csv format. Pivoted tables are read back from
        this path
    :param name: name for the root table
    :param options: dict of optional parameters for relationalize
    :param transformation_ctx: context key to retrieve metadata about the current transformation
    :param info: String, any string to be associated with errors in this transformation.
    :param stageThreshold: Long, number of errors in the given transformation for which the processing needs to error out.
    :param totalThreshold: Long, total number of errors upto and including in this transformation
      for which the processing needs to error out.
    :return: DynamicFrameCollection
    """

    # TODO: Make staging_path a mandatory argument
    def __call__(self, frame, staging_path=None, name='roottable', options=None, transformation_ctx = "", info="",
        stageThreshold=0, totalThreshold=0):
        options = options or {}
        # TODO: Remove special handling of staging_path and make it mandatory after TempDir is made a mandatory argument
        # We are directly accessing the args variable assuming that it is available in the global scope. This is to
        # maintain backward compatibility with the relationalize call that did not have the mandatory staging_path arg
        if staging_path is None:
            if _global_args['TempDir'] is not None and _global_args['TempDir'] != "":
                staging_path = _global_args['TempDir']
            else:
                raise RuntimeError("Unable to set staging_path using args "+str(_global_args))
        return frame.relationalize(name, staging_path, options, transformation_ctx, info, stageThreshold, totalThreshold)

    @classmethod
    def describeArgs(cls):
        arg1 = {"name": "frame",
                "type": "DynamicFrame",
                "description": "The DynamicFrame to relationalize",
                "optional": False,
                "defaultValue": None}
        arg2 = {"name": "staging_path",
                "type": "String",
                "description": "path to store partitions of pivoted tables in csv format",
                "optional": True,
                "defaultValue": None}
        arg3 = {"name": "name",
                "type": "String",
                "description": "Name of the root table",
                "optional": True,
                "defaultValue": "roottable"}
        arg4 = {"name": "options",
                "type": "Dictionary",
                "description": "dict of optional parameters for relationalize",
                "optional": True,
                "defaultValue": "{}"}
        arg5 = {"name": "transformation_ctx",
                "type": "String",
                "description": "A unique string that is used to identify stats / state information",
                "optional": True,
                "defaultValue": ""}
        arg6 = {"name": "info",
                "type": "String",
                "description": "Any string to be associated with errors in the transformation",
                "optional": True,
                "defaultValue": "\"\""}
        arg7 = {"name": "stageThreshold",
                "type": "Integer",
                "description": "Max number of errors in the transformation until processing will error out",
                "optional": True,
                "defaultValue": "0"}
        arg8 = {"name": "totalThreshold",
                "type": "Integer",
                "description": "Max number of errors total until processing will error out.",
                "optional": True,
                "defaultValue": "0"}

        return [arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8]

    @classmethod
    def describeTransform(cls):
        return "Flatten nested schema and pivot out array columns from the flattened frame"

    @classmethod
    def describeErrors(cls):
        return []

    @classmethod
    def describeReturn(cls):
        return {"type": "DynamicFrameCollection",
                "description": "DynamicFrameCollection resulting from Relationalize call"}
