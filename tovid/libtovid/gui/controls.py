# controls.py

import wx

import libtovid
from libtovid.gui.util import VER_GetFirstChild

__all__ = [\
    "BoldToggleButton",
    "FlexTreeCtrl",
    "HeadingText"]

class BoldToggleButton(wx.ToggleButton):
    """A wx.ToggleButton with bold font"""
    def __init__(self, parent, id, label):
        wx.ToggleButton.__init__(self, parent, id, label,
            wx.DefaultPosition, wx.Size(-1, 40))
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD)
        self.SetFont(font)


class FlexTreeCtrl(wx.TreeCtrl):
    """A more flexible tree control, with support for moving and copying
    branches."""

    def __init__(self, parent, id, pos = wx.DefaultPosition,
        size = wx.DefaultSize, style = wx.TR_HAS_BUTTONS,
        validator = wx.DefaultValidator, name = "FlexTreeCtrl"):
        wx.TreeCtrl.__init__(self, parent, id, pos, size, style, validator, name)
        """Initialize FlexTreeCtrl."""

    def CopyChildren(self, dest, src, recursively = True):
        """Copy all children of src to dest. Recurse if desired."""
        # Get the first child
        nextChild, cookie = VER_GetFirstChild(self, src)
        # As long as there are more children, append them to dest
        while nextChild.IsOk():
            newChild = self.AppendItem(dest,
                self.GetItemText(nextChild),
                self.GetItemImage(nextChild),
                self.GetItemImage(nextChild, wx.TreeItemIcon_Selected))
            self.SetPyData(newChild, self.GetPyData(nextChild))
            # If the child has children of its own and recursive is
            # True, call CopyChildren on this child
            if recursively and self.ItemHasChildren(nextChild):
                self.CopyChildren(newChild, nextChild, True)
            # Get the next child
            nextChild, cookie = self.GetNextChild(src, cookie)

    def MoveChildren(self, dest, src, recursively = True):
        """Recursively move all children of src to dest."""
        self.CopyChildren(dest, src, recursively)
        self.DeleteChildren(src)

    def AppendItemCopy(self, parent, src, recursively = True):
        """Append a copy of src under parent. Copy all children, and recurse if
        desired.  Returns the wx.TreeItemId of the copy, or an invalid item if
        something went wrong."""
        # Make sure parent and src are valid
        if not parent.IsOk() or not src.IsOk():
            return wx.TreeItemId()
        # Create a new copy of src under parent
        newItem = self.AppendItem(parent, self.GetItemText(src),
            self.GetItemImage(src), self.GetItemImage(src, wx.TreeItemIcon_Selected))
        self.SetPyData(newItem, self.GetPyData(src))
        # Copy children, recurse if desired
        self.CopyChildren(newItem, src, recursively)
        # Return the new copy
        return newItem

    def PrependItemCopy(self, parent, src, recursively = True):
        """Prepend a copy of src under parent. Copy all children, and recurse
        if desired.  Returns the wx.TreeItemId of the copy, or an invalid item
        if something went wrong."""
        # Make sure parent and src are valid
        if not parent.IsOk() or not src.IsOk():
            return wx.TreeItemId()
        # Create a new copy of src under parent
        newItem = self.PrependItem(parent, self.GetItemText(src),
            self.GetItemImage(src),
            self.GetItemImage(src, wx.TreeItemIcon_Selected))
        self.SetPyData(newItem, self.GetPyData(src))
        # Copy children, recurse if desired
        self.CopyChildren(newItem, src, recursively)
        # Return the new copy
        return newItem

    def InsertItemCopy(self, parent, src, prev, recursively = True):
        """Insert a copy of src under parent, after prev. Copy all children,
        and recurse if desired.  Returns the wx.TreeItemId of the copy, or an
        invalid item if something went wrong."""
        # Make sure parent, src, and prev are valid
        if not parent.IsOk() or not src.IsOk() or not prev.IsOk():
            return wx.TreeItemId()
        # Make sure prev is a child of parent
        if self.GetItemParent(prev) != parent:
            return wx.TreeItemId()
        # Create a new copy of src under parent
        newItem = self.InsertItem(parent, prev, self.GetItemText(src),
            self.GetItemImage(src),
            self.GetItemImage(src, wx.TreeItemIcon_Selected))
        self.SetPyData(newItem, self.GetPyData(src))
        # Copy children, recurse if desired
        self.CopyChildren(newItem, src, recursively)
        # Return the new copy
        return newItem

    def AppendItemMove(self, parent, src):
        """Move src, and all its descendants, under parent, at the end of
        parent's children.  If src is an ancestor of parent, do nothing.
        Returns the wx.TreeItemId of the copy, or an invalid item if something
        went wrong."""
        # If src is an ancestor of parent, return. (Cannot move
        # a branch into its own sub-branch)
        if self.ItemIsAncestorOf(src, parent):
            return wx.TreeItemId()
        # Copy src to parent and recurse
        newItem = self.AppendItemCopy(parent, src, True)
        # Delete src and all its children
        self.Delete(src)
        return newItem

    def PrependItemMove(self, parent, src):
        """Move src, and all its descendants, under parent, at the beginning of
        parent's children.  If src is an ancestor of parent, do nothing.
        Returns the wx.TreeItemId of the copy, or an invalid item if something
        went wrong."""
        # If src is an ancestor of parent, return. (Cannot move
        # a branch into its own sub-branch)
        if self.ItemIsAncestorOf(src, parent):
            return wx.TreeItemId()
        # Copy src to parent and recurse
        newItem = self.PrependItemCopy(parent, src, True)
        # Delete src and all its children
        self.Delete(src)
        return newItem

    def InsertItemMove(self, parent, src, prev):
        """Move src, and all its descendants, under parent, after parent's
        child prev.  If src is an ancestor of parent, do nothing.  Returns the
        wx.TreeItemId of the copy, or an invalid item if something went
        wrong."""
        # If src is an ancestor of parent, return. (Cannot move
        # a branch into its own sub-branch)
        if self.ItemIsAncestorOf(src, parent):
            return wx.TreeItemId()
        # Copy src to parent and recurse
        newItem = self.InsertItemCopy(parent, src, prev, True)
        # Delete src and all its children
        self.Delete(src)
        return newItem

    def ItemIsAncestorOf(self, item1, item2):
        """Return True if item1 is an ancestor of item2, False otherwise"""
        curAncestor = self.GetItemParent(item2)
        while curAncestor.IsOk():
            if curAncestor == item1:
                return True
            curAncestor = self.GetItemParent(curAncestor)

        # Root was reached and item1 was not found
        return False

    def MoveItemUp(self):
        """Move the currently-selected item up in the list.  Item stays within
        its group of siblings."""
        curItem = self.GetSelection()
        prevItem = self.GetPrevSibling(curItem)
        parentItem = self.GetItemParent(curItem)
        # If previous sibling is OK, move-insert the previous
        # sibling after the current item
        if prevItem.IsOk():
            newItem = self.InsertItemMove(parentItem, prevItem, curItem)
            if newItem.IsOk():
                self.SelectItem(curItem)

    def MoveItemDown(self):
        """Move the currently-selected item down in the list.  Item stays
        within its group of siblings."""
        curItem = self.GetSelection()

        nextItem = self.GetNextSibling(curItem)
        parentItem = self.GetItemParent(curItem)
        # If next sibling is OK, move-insert current item
        # after next sibling
        if nextItem.IsOk():
            newItem = self.InsertItemMove(parentItem, curItem, nextItem)
            if newItem.IsOk():
                self.SelectItem(newItem)

    def Delete(self, item):
        """Overridden Delete() function. Intelligently selects the previous
        item prior to deletion."""
        lastItem = item
        curParent = self.GetItemParent(item)
        prevSib = self.GetPrevSibling(lastItem)
        wx.TreeCtrl.Delete(self, lastItem)
        # Select the previous sibling, or the parent if
        # there was no previous sibling
        if prevSib.IsOk():
            self.SelectItem(prevSib)
        else:
            self.SelectItem(curParent)

    def GetReferenceList(self, topItem):
        """Returns a list of all data references in the branch descending from
        topItem."""
        # If topItem is not OK, just return
        if not topItem.IsOk():
            return
        refs = []
        # Append topItem's data
        refs.append(self.GetPyData(topItem))
        # Recursively append children
        child, cookie = VER_GetFirstChild(self, topItem)
        while child.IsOk():
            # If item has children, recurse
            if self.ItemHasChildren(child):
                grandchildren = self.GetReferenceList(child)
                refs.extend(grandchildren)
            # Otherwise, just append this item
            else:
                refs.append(self.GetPyData(child))

            # Get the next child
            child, cookie = self.GetNextChild(topItem, cookie)
        # Return the results
        return refs

    def GetItemList(self, topItem):
        """Returns a list of all Items in the branch descending from topItem."""
        # If topItem is not OK, just return
        if not topItem.IsOk():
            return
        items = []
        # Append topItem's data
        items.append(topItem)
        # Recursively append children
        child, cookie = VER_GetFirstChild(self, topItem)
        while child.IsOk():
            # If item has children, recurse
            if self.ItemHasChildren(child):
                grandchildren = self.GetItemList(child)
                items.extend(grandchildren)
            # Otherwise, just append this item
            else:
                items.append(child)

            # Get the next child
            child, cookie = self.GetNextChild(topItem, cookie)
        # Return the results
        return items

class HeadingText(wx.StaticText):
    """A large, bold static text control to use for headings"""
    def __init__(self, parent, id, label):
        wx.StaticText.__init__(self, parent, id, label)
        font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD)
        self.SetFont(font)

