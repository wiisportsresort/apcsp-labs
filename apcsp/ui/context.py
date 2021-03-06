from typing import TYPE_CHECKING, Any, Dict, List, Set

from apcsp.ui import form, selectable

if TYPE_CHECKING:
    from apcsp.ui import menu


class MenuContext(object):
    data: Dict[str, Any]
    selected = property(lambda self: self.menu.selected)

    def __init__(
        self,
        menu: "menu.Menu | None" = None,
        *,
        parent: "MenuContext | None" = None,
        data: Dict[str, Any] = None,
    ):
        self.menu = menu
        self.parent = parent
        self.data = data or parent.data if parent else {}
        self.exit_next = False

    def check_fields(self) -> Dict[str, form.FormField]:
        assert self.menu, "No menu available"
        objects: Dict[str, form.FormField] = {}
        for field in self.menu.fields:
            if field.id in objects:
                raise ValueError(
                    f'Field id "{field.id}" is shared by fields'
                    f" {objects[field.id].__class__} and {field.__class__}"
                )
            objects[field.id] = field
        return objects

    def run(self, menu: "menu.Menu | None" = None) -> None:
        self.menu = menu or self.menu

        assert self.menu, "No menu available"
        if self.exit_next:
            return

        self.check_fields()
        self.menu.run(self)

    def fork(self, menu: "menu.Menu | None" = None) -> "MenuContext":
        return self.__class__(menu, parent=self)

    def redraw(self, clear: bool = True) -> None:
        assert self.menu, "No menu available"
        self.menu.print(self, clear)

    def exit(self) -> None:
        self.exit_next = True

    def replace(self, menu: "menu.Menu") -> None:
        self.exit()
        if self.parent is None:
            raise ValueError("Cannot replace the root menu")
        new_context = self.parent.fork()
        new_context.run(menu)

    def submit(self) -> selectable.FormResult | None:
        assert self.menu, "No menu available"
        if not self.menu.fields:
            print("WARNING: No fields in form")
            return {}

        self.check_fields()
        success = True
        for field in self.menu.fields:
            result = field.validate(self)
            success = success and result

        if not success:
            self.redraw()
            return None

        data: selectable.FormResult = {}
        for field in self.menu.fields:
            data[field.id] = field

        return data
