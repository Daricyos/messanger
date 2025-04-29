/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { useService } from "@web/core/utils/hooks";

export class CustomKanbanController extends KanbanController {
    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    async _onOpenWizard() {
        const action = {
            name: "Mailing list",
            type: "ir.actions.act_window",
            res_model: "sms.exting",
            views: [[false, "form"]],
            target: 'new',
        };
        this.actionService.doAction(action);
    }
}

registry.category("views").add("custom_kanban", {
    ...kanbanView,
    Controller: CustomKanbanController,
    buttonTemplate: "messenger.KanbanView.Buttons",
});
