import graphene
from graphene_django import DjangoObjectType
# from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay

from account.models import CustomUser
from todoapp.models import Todo


class AccountType(DjangoObjectType):
    class Meta:
        model = CustomUser
        exclude = ('password',)

    def resolve_post(self, info):
        return Todo.objects.filter(owner=self)

    @classmethod
    def get_node(cls, self, id):
        return AccountType.objects.get(id=id)


class TodoType(DjangoObjectType):
    class Meta:
        model = Todo
        fields = "__all__"
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    all_account = graphene.List(AccountType)
    logged_in_user = graphene.Field(AccountType)
    all_todo = graphene.List(TodoType)
    todo = graphene.Field(TodoType, todo_id=graphene.Int())

    def resolve_all_todo(self, info, **kwargs):
        return Todo.objects.all()

    def resolve_todo(self, info, todo_id):
        return Todo.objects.get(pk=todo_id)


class TodoInput(graphene.InputObjectType):
    id = graphene.ID()
    owner = graphene.ID()
    title = graphene.String()
    body = graphene.String()
    created = graphene.DateTime()
    completed = graphene.Boolean()


class CreateTodo(graphene.Mutation):
    class Arguments:
        todo_data = TodoInput(required=True)

    todo = graphene.Field(TodoType)

    @staticmethod
    def mutate(root, info, todo_data=None):
        owner = CustomUser.objects.get(pk=todo_data.owner)

        todo_instance = Todo(
            title=todo_data.title,
            owner=owner,
            body=todo_data.body,
            created=todo_data.created,
            completed=todo_data.completed,
        )

        todo_instance.save()

        return CreateTodo(todo=todo_instance)


class Mutation(graphene.ObjectType):
    create_todo = CreateTodo.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
