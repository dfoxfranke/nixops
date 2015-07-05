{ config, lib, uuid, name, ... }:
with lib;
{
  options = {
    apiKeyfile = mkOption {
      default = "";
      type = types.str;
      description = "Linode API Key.";
    };
  
    label = mkOption {
      default = "charon-${uuid}-${name}";
      type = types.str;
      description = "The label for this StackScript.";
    };

    description = mkOption {
      default = "";
      type = types.str;
      description = "A description of this StackScript.";
    };

    distributionIDList = mkOption {
      default = [60 78 86 87 117 118 120 122 124 126 127 129 130 132 133 134 135 137 138 139 140 141];
      type = types.listOf types.int;
      description = "List of DistributionIDs that this script works on.";
    };

    isPublic = mkOption {
      default = false;
      type = types.bool;
      description = "Whether this StackScript is published in the Library, for everyone to use.";
    };

    revNote = mkOption {
      default = "";
      type = types.str;
      description = "Revision note.";
    };

    script = mkOption {
      default = "";
      type = types.str;
      description = "Text of the script.";
    };
  };
}
    
