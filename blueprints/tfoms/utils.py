# -*- encoding: utf-8 -*-
from models import TagsTree

def get_tree(template_id, root, level, tree):
    """Построение дерева по корню"""
#    level = 0
#    tree = [[root, level]]
    
    children = TagsTree.query.filter_by(template_id=template_id).filter_by(parent_id=root.tag_id).join(TagsTree.tag).all()
    #children = session.query(models.TagsTree.teg_id, models.TagsTree.parent_d).filter_by(parent_id=root[0])
    if children:
        level = level + 1
        for child in children:
            tree.append([child, level])
            get_tree(template_id, child, level, tree)
    return tree