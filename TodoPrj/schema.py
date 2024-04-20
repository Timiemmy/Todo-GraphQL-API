import graphene
from graphene_django import DjangoObjectType
# from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay
# import graphql_jwt
from graphql_jwt.decorators import login_required

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

    @login_required
    def resolve_all_todo(self, info, **kwargs):
        user = info.context.user
        return Todo.objects.filter(owner=user)

    @login_required
    def resolve_todo(self, info, todo_id):
        user = info.context.user
        try:
            todo = Todo.objects.get(pk=todo_id, owner=user)
            return Todo.objects.get(pk=todo_id)
        except Todo.DoesNotExist:
            return None


class UserInput(graphene.InputObjectType):
    id = graphene.ID()
    email = graphene.String()
    username = graphene.String()
    password = graphene.String()


class CreateUser(graphene.Mutation):
    class Arguments:
        user_data = UserInput(required=True)

    user = graphene.Field(AccountType)

    @staticmethod
    def mutate(self, info, user_data=None):
        user_instance = CustomUser(
            email=user_data.email,
            username=user_data.username,
        )
        user_instance.set_password(user_data.password)
        user_instance.save()

        return CreateUser(user=user_instance)

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



class UpdateTodo(graphene.Mutation):
    class Arguments:
        todo_data = TodoInput(required=True)

    todo = graphene.Field(TodoType)

    @staticmethod
    def mutate(root, info, todo_data=None):
        try:
            # Attempt to retrieve the Todo instance by ID
            todo_instance = Todo.objects.get(pk=todo_data.id)
            owner = CustomUser.objects.get(username=todo_data.owner)
            # Update the fields if the Todo instance exists
            todo_instance.title = todo_data.title
            todo_instance.owner = owner
            todo_instance.body = todo_data.body
            todo_instance.save()

            return UpdateTodo(todo=todo_instance)

        except Todo.DoesNotExist:
            # Handle the case where the specified todo doesn't exist
            return UpdateTodo(post=None)
        

class DeleteTodo(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    todo = graphene.Field(TodoType)

    @staticmethod
    def mutate(root, info, id):
        todo_instance = Todo.objects.get(pk=id)
        todo_instance.delete()

        return None

class Mutation(graphene.ObjectType):
    create_todo = CreateTodo.Field()
    update_todo = UpdateTodo.Field()
    delete_todo = DeleteTodo.Field()
    create_user = CreateUser.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
