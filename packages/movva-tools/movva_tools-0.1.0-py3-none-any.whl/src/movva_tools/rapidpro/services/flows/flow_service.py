from rapidpro.database.flows import RapidProFlows, RapidProFlowsRevision
from rapidpro.database.organization import RapidProOrganization
from rapidpro.database.users import RapidProUser
from rapidpro.databases import RapidProDatabase
from rapidpro.exceptions.object_does_not_exist_exception import ObjectDoesNotExistException
from rapidpro.constants import DEFAULT_USER_ID, Flow, FlowType, GoFlowTypes
from rapidpro.services.base_service import BaseService
from rapidpro.services.organization.organization_service import OrganizationService
from rapidpro.services.user.user_service import UserService
from rapidpro.validators.flow_name_validator import FlowNameValidator


class FlowService(BaseService):

    def __init__(self, db_connection=None) -> None:

        super().__init__(db_connection=db_connection)

        # model table entities
        self.flow = RapidProFlows
        self.flow_revision = RapidProFlowsRevision
        self.org = RapidProOrganization

        # services
        self.user_service = UserService(
            db_connection=self.db_connection
        )
        self.organization_service = OrganizationService(
            db_connection=self.db_connection
        )

    def __set_default_flow_metadata(self):

        return {
            "results": [],
            "dependencies": [],
            "waiting_exit_uuids": [],
            "parent_refs": []
        }

    def __set_initial_flow_revision_definition(self, flow):
        return {
            Flow.DEFINITION_NAME: flow.name,
            Flow.DEFINITION_UUID: str(flow.uuid),
            Flow.DEFINITION_SPEC_VERSION: Flow.CURRENT_SPEC_VERSION,
            Flow.DEFINITION_LANGUAGE: Flow.BASE_LANGUAGE,
            Flow.DEFINITION_TYPE: GoFlowTypes.TYPE_MESSAGE,
            Flow.DEFINITION_NODES: [],
            Flow.DEFINITION_UI: {},
            Flow.DEFINITION_REVISION: 1,
            Flow.DEFINITION_EXPIRE_AFTER_MINUTES: Flow.EXPIRES_AFTER_MINUTES
        }

    def __set_flow_revision_definition(self, flow, setted_definition):

        setted_definition[Flow.DEFINITION_NAME] = flow.name
        setted_definition[Flow.DEFINITION_REVISION] = 1
        setted_definition[Flow.DEFINITION_UUID] = str(flow.uuid)

        return setted_definition

    def is_valid_name(cls, name: str) -> bool:
        try:
            FlowNameValidator()(value=name)
            return True
        except Exception:
            return False

    def get_flow(self, flow_name):

        flow = self.db_connection.session.query(self.flow).filter_by(
            name=flow_name
        ).first()

        if flow:
            return flow
        else:
            raise ObjectDoesNotExistException(dababase_object=self.flow)

    def create_new_flow_revision(self, flow, user, setted_definition=None):
        if setted_definition:
            definition = self.__set_flow_revision_definition(
                flow, setted_definition=setted_definition
            )
        else:
            definition = self.__set_initial_flow_revision_definition(flow=flow)

        new_flow_revision = self.flow_revision(
            created_by_id=user.id,
            flow_id=flow.id,
            definition=definition
        )

        self.add(new_flow_revision)
        self.flush()
        return new_flow_revision

    def _create_flow(
        self,
        org_name,
        flow_name,
        flow_type=FlowType.TYPE_MESSAGE,
        expires_after_minutes=Flow.EXPIRES_AFTER_MINUTES,
        create_revision: bool = False,
        external_context: bool = False
    ):
        new_flow_revision = None
        user = self.user_service.get_default_user()
        org = self.organization_service.get_org(org_name)

        new_flow = self.flow(
            org_id=org.id,
            created_by_id=user.id,
            name=flow_name,
            flow_type=flow_type,
            expires_after_minutes=expires_after_minutes,
            flow_metadata=self.__set_default_flow_metadata()
        )

        self.add(new_flow)
        self.flush()

        if create_revision:
            new_flow_revision = self.create_new_flow_revision(
                flow=new_flow,
                user=user
            )

        return new_flow, new_flow_revision

    def create(
        self,
        org_name,
        flow_name,
        flow_type=FlowType.TYPE_MESSAGE,
        expires_after_minutes=Flow.EXPIRES_AFTER_MINUTES,
        create_revision: bool = False,
        commit_after_create: bool = False,
        external_context: bool = True
    ):

        self.is_valid_name(flow_name)

        if not external_context:

            with self.db_connection.session.begin():
                new_flow, new_flow_revision = self._create_flow(
                    org_name=org_name,
                    flow_name=flow_name,
                    flow_type=flow_type,
                    expires_after_minutes=expires_after_minutes,
                    create_revision=create_revision,
                    external_context=external_context
                )
        else:
            new_flow, new_flow_revision = self._create_flow(
                org_name=org_name,
                flow_name=flow_name,
                flow_type=flow_type,
                expires_after_minutes=expires_after_minutes,
                create_revision=create_revision,
                external_context=external_context
            )

        if commit_after_create:
            # Commit a transação após os blocos 'with'
            self.commit()

        return new_flow, new_flow_revision
