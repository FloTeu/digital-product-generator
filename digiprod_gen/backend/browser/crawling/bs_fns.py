from bs4.element import Tag

# Function to check if a tag or its children have a specific class
def tag_or_children_have_class(tag: Tag, class_name: str):
    # Check if the tag itself has the class
    if class_name in tag.get('class', []):
        return True

    # Check the children recursively
    for child in tag.children:
        if child.name:
            if tag_or_children_have_class(child, class_name):
                return True

    return False