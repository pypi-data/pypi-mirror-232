from typing import ClassVar

from attrs import define, field

from resotolib.json import value_in_path
from resotolib.types import Json

default_config: Json = {
    "default": {"expiration": "24h"},
    "kinds": [
        "aws_ec2_instance",
        "aws_vpc",
        "aws_cloudformation_stack",
        "aws_elb",
        "aws_alb",
        "aws_alb_target_group",
        "aws_eks_cluster",
        "aws_eks_nodegroup",
        "aws_ec2_nat_gateway",
    ],
    "accounts": {
        "aws": {
            "123465706934": {"name": "eng-audit"},
            "123479172032": {"name": "eng-devprod"},
            "123453451782": {"name": "sales-lead-gen", "expiration": "12h"},
            "123415487488": {"name": "sales-hosted-lead-gen", "expiration": "8d"},
        },
    },
}


@define
class TagValidatorConfig:
    kind: ClassVar[str] = "plugin_tagvalidator"
    enabled: bool = field(
        default=False,
        metadata={"description": "Enable plugin?", "restart_required": True},
    )
    dry_run: bool = field(
        default=False,
        metadata={"description": "Dry run"},
    )
    config: Json = field(
        factory=lambda: default_config,
        metadata={
            "description": (
                "Configuration for the plugin\n"
                "See https://github.com/someengineering/resoto/tree/main/plugins/tagvalidator for syntax details"
            )
        },
    )

    @staticmethod
    def validate(cfg: "TagValidatorConfig") -> bool:
        config = cfg.config
        required_sections = ["kinds", "accounts"]
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Section '{section}' not found in config")

        if not isinstance(config["kinds"], list) or len(config["kinds"]) == 0:
            raise ValueError("Error in 'kinds' section")

        if not isinstance(config["accounts"], dict) or len(config["accounts"]) == 0:
            raise ValueError("Error in 'accounts' section")

        maybe_default_expiration = value_in_path(config, ["default", "expiration"])
        for cloud_id, account in config["accounts"].items():
            for account_id, account_data in account.items():
                if "name" not in account_data:
                    raise ValueError(f"Missing 'name' for account '{cloud_id}/{account_id}")
                if account_data.get("expiration") is None and maybe_default_expiration is None:
                    raise ValueError(
                        f"Missing 'expiration' for account '{cloud_id}/{account_id}'"
                        "and no default expiration defined"
                    )
        return True
