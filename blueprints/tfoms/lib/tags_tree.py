# -*- encoding: utf-8 -*-
from blueprints.tfoms.models import TagsTree


class TagTree():

    def __init__(self, root, template_id):
        self.root = root
        self.template_id = template_id

    def get_node_children(self, node):
        children_values = TagsTree.query.filter_by(template_id=self.template_id).\
            filter_by(parent_id=node.value.tag_id).join(TagsTree.tag).all()
        return [TagTreeNode(value, node.level + 1) for value in children_values]

    def load_tree(self, root, tree):
        """Построение дерева по корню"""

        children = self.get_node_children(root)
        if children:
            for child in children:
                tree.append(child)
                self.load_tree(child, tree)
        return tree


class TagTreeNode():
    def __init__(self, value, level):
        self.value = value
        self.level = level