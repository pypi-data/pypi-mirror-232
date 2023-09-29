import json
from rapidpro.database.contacts import RapidProContactFields
from rapidpro.database.flows import RapidProFlowsRevision
from rapidpro.constants import MAX_NAME_LEN
from rapidpro.exceptions.object_does_not_exist_exception import ObjectDoesNotExistException
from rapidpro.exceptions.object_does_not_updated_exception import ObjectDoesNotUpdatedExeption
from rapidpro.services.base_service import BaseService
from rapidpro.services.flows.flow_service import FlowService
from sqlalchemy import desc, update

from rapidpro.services.organization.organization_service import OrganizationService
from rapidpro.services.user.user_service import UserService
from rapidpro.decorators.database import ensure_transaction
import pandas as pd
from typing import List


class FlowCopyService(BaseService):

    def __init__(self, db_connection=None) -> None:

        super().__init__(db_connection)

        # services
        self.flow_service = FlowService(
            db_connection=self.db_connection
        )
        self.organization_service = OrganizationService(
            db_connection=self.db_connection
        )
        self.user_service = UserService(
            db_connection=self.db_connection
        )

        # model table entities
        self.contact_field = RapidProContactFields
        self.flow_revision = RapidProFlowsRevision

    def get_unique_name(self, org, base_name):

        name = f'{base_name[:MAX_NAME_LEN]}' if len(base_name) > MAX_NAME_LEN else base_name
        qs = self.db_connection.session.query(self.flow).filter_by(
            org_id=org.id,
            is_active=True,
            name=name
        ).all()

        if qs:
            name = 'Copy_of ' + name

        return name

    def get_last_flow_revision(self, flow):

        flow_revision = self.db_connection.session.query(
            self.flow_revision
        ).order_by(
            desc(self.flow_revision.created_on)
        ).filter_by(
            flow_id=flow.id
        ).first()

        if flow_revision:
            return flow_revision
        else:
            raise ObjectDoesNotExistException(
                dababase_object=self.flow_revision
            )

    def transfer_flow_revision_messages(self, json_string: str, df: pd.DataFrame):
        messages = df.loc[:, ['MENSAGENS ORIGINAIS', 'MENSAGENS NOVAS']]
        messages = messages.dropna(how='all')

        if messages.empty:
            raise Exception('Without Messages.')

        for _, actual, new in messages.itertuples():
            actual = actual.replace('\n', '\\n')
            new = new.replace('\n', '\\n')
            actual = f'"{actual}"'
            new = f'"{new}"'
            json_string = json_string.replace(actual, new)

        return json_string

    def transfer_flow_revision_data(self, flow_json: dict, spreadsheet_data: pd.DataFrame):
        flow_data = json.dumps(flow_json, ensure_ascii=False)

        flow_data = self.transfer_flow_revision_messages(
            json_string=flow_data,
            df=spreadsheet_data
        )
        return json.loads(flow_data)

    def migrate_definition(
        self, flow_json, flow, flow_revision_destination, user,
        data: pd.DataFrame = None
    ):
        flow_revision_copy = flow_json.copy()

        # aqui deve entrar as modificações do flow revision
        if not data.empty:
            flow_revision_copy = self.transfer_flow_revision_data(
                spreadsheet_data=data,
                flow_json=flow_revision_copy
            )

        if flow_revision_destination:
            definition_destination = json.loads(
                flow_revision_destination.definition
            )
            flow_revision_copy['name'] = definition_destination['name']

            flow_revision_copy_json = json.dumps(flow_revision_copy)

            query = update(
                self.flow_revision
            ).where(
                self.flow_revision.id == flow_revision_destination.id
            ).values(
                definition=flow_revision_copy_json
            ).returning(self.flow_revision)

            if result := self.db_connection.execute_query(query).fetchone():
                return result
            else:
                raise ObjectDoesNotUpdatedExeption(
                    dababase_object=self.flow_revision
                )
        else:
            flow_revision_destination = self.flow_service.create_new_flow_revision(
                flow=flow, user=user,
                setted_definition=flow_revision_copy
            )

        return flow_revision_destination.definition

    def import_definition(
        self,
        user, definition,
        flow_destination, flow_revision_destination, org_destination,
        data: pd.DataFrame = None
    ):
        """
            Allows setting the definition for a flow from another definition.
            All UUID's will be remapped.
        """

        flow_revision_migrated_data = self.migrate_definition(
            flow_json=definition,
            flow=flow_destination,
            user=user,
            flow_revision_destination=flow_revision_destination,
            data=data
        )

        flow_revision_migrated = self.get_last_flow_revision(
            flow=flow_destination
        )

        return flow_revision_migrated

    def get_definition(self, flow) -> dict:
        revision = self.get_last_flow_revision(
            flow=flow
        )

        definition = revision.definition

        return json.loads(definition)

    @ensure_transaction
    def clone(self, base_flow_name, flow_suggested_name, destiny_organization_name, data: List[List[str]] = None):
        """
        Returns a clone of this flow
        """
        if data:
            data = pd.DataFrame(data[1:], columns=data[0])

        with self.db_connection.session.begin():
            user = self.user_service.get_default_user()
            org = self.organization_service.get_org(
                org_name=destiny_organization_name
            )

            copy, revision = self.flow_service.create(
                org_name=org.name,
                flow_name=flow_suggested_name
            )

            base_flow = self.flow_service.get_flow(
                flow_name=base_flow_name
            )

            base_flow_json = self.get_definition(
                flow=base_flow
            )

            self.import_definition(
                user=user,
                definition=base_flow_json,
                flow_destination=copy,
                flow_revision_destination=revision,
                org_destination=org,
                data=data
            )
