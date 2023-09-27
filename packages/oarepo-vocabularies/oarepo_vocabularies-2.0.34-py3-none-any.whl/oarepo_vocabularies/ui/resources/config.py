import marshmallow as ma
from flask import current_app
from invenio_records_resources.services import Link, pagination_links
from oarepo_ui.resources.config import RecordsUIResourceConfig
from oarepo_ui.resources.links import UIRecordLink

from oarepo_vocabularies.ui.resources.components import (
    DepositVocabularyOptionsComponent,
    VocabularyRecordsComponent,
)


class InvenioVocabulariesUIResourceConfig(RecordsUIResourceConfig):
    template_folder = "../templates"
    url_prefix = "/vocabularies/"
    blueprint_name = "oarepo_vocabularies_ui"
    ui_serializer_class = (
        "oarepo_vocabularies.resources.records.ui.VocabularyUIJSONSerializer"
    )
    api_service = "vocabularies"
    layout = "oarepo_vocabularies_ui"

    templates = {
        "detail": {
            "layout": "oarepo_vocabularies_ui/VocabulariesDetail.jinja",
            "blocks": {
                "record_sidebar": "VocabulariesSidebar",
            },
        },
        "search": {"layout": "oarepo_vocabularies_ui/search.html"},
        "create": {"layout": "oarepo_vocabularies_ui/form.html"},
        "edit": {"layout": "oarepo_vocabularies_ui/form.html"},
    }

    routes = {
        "create": "/<vocabulary_type>/_new",
        "edit": "/<vocabulary_type>/<pid_value>/edit",
        "search": "/<vocabulary_type>/",
        "detail": "/<vocabulary_type>/<pid_value>",
        "export": "/<vocabulary_type>/<pid_value>/export/<export_format>",
    }

    components = [VocabularyRecordsComponent, DepositVocabularyOptionsComponent]

    request_vocabulary_type_args = {"vocabulary_type": ma.fields.Str()}

    ui_links_item = {
        "self": UIRecordLink("{+ui}{+url_prefix}{vocabulary_type}/{id}"),
        "edit": UIRecordLink("{+ui}{+url_prefix}{vocabulary_type}/{id}/edit"),
        "search": UIRecordLink("{+ui}{+url_prefix}{vocabulary_type}/"),
    }

    @property
    def ui_links_search(self):
        return {
            **pagination_links("{+ui}{+url_prefix}{vocabulary_type}/{?args*}"),
            "create": Link("{+ui}{+url_prefix}{vocabulary_type}/_new"),
        }

    def vocabulary_props_config(self, vocabulary_type):
        return current_app.config.get("INVENIO_VOCABULARY_TYPE_METADATA", {}).get(
            vocabulary_type, {}
        )
