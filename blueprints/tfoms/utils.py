# -*- encoding: utf-8 -*-

def get_tree(root):
    """Построение дерева по корню"""
    level = 0
    tree = [[root, level]]
    children = session.query(models.TagsTree.teg_id, models.TagsTree.parent_d).filter_by(parent_id=root[0])
    if children:
        level = level + 1
        for cild in children:
            tree.append[[child, level]]
            get_tree(child)
    return tree