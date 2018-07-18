from OxygenRM.internals.QueryBuilder import QueryBuilder
from OxygenRM.internals.ModelContainer import ModelContainer

class HasQueryBuilder(QueryBuilder):
    def __init__(self, target_model, parting_model, relation):
        super().__init__(target_model.table_name, target_model)

        self.parting_model = parting_model
        self.on_self_col = relation.on_self_col
        self.on_other_col = relation.on_other_col
        self.how_much = relation.how_much
        self.table_name = target_model.table_name

        self.where(self.on_other_col, '=', getattr(parting_model, self.on_self_col))

    # HAS One
    def assign(self, other_model):
        other_id = other_model.get_primary()
        self_id = getattr(self.parting_model, self.on_self_col)

        def pending_function():
            QueryBuilder.table(self.table_name).where(self.on_other_col, '=', self_id).update({self.on_other_col: None})
            QueryBuilder.table(self.table_name).where(other_model.primary, '=', other_id).update({self.on_other_col: self_id})

        self.parting_model._rel_queue.append(pending_function)

    def deassign(self):
        self_id = getattr(self.parting_model, self.on_self_col)

        def pending_function():
            QueryBuilder.table(self.table_name).where(self.on_other_col, '=', self_id).update({self.on_other_col: None})

        self.parting_model._rel_queue.append(pending_function)

    # HAS MANY
    def add(self, other_model):
        other_id = other_model.get_primary()
        self_id = getattr(self.parting_model, self.on_self_col)

        def pending_function():
            QueryBuilder.table(self.table_name).where(other_model.primary, '=', other_id).update({self.on_other_col: other_id})
        
        self.parting_model._rel_queue.append(pending_function)

    def add_many(self, other_models):
        self_id = getattr(self.parting_model, self.on_self_col)

        def pending_function():
            QueryBuilder.table(self.table_name).or_where_many(
                (model.primary, '=', model.get_primary()) for model in other_models 
            ).update({self.on_other_col: self_id})
        
        self.parting_model._rel_queue.append(pending_function)

    def remove_all(self):
        self.deassign()

    def reassign(self, other_models):
        self.deassign()
        self.add_many(other_models)