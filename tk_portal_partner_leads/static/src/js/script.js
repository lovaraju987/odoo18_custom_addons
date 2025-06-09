/** @odoo-module **/

import { rpc } from "@web/core/network/rpc";

$(document).ready(async function () {
  /*** Get state using country ***/
    $("#country").on("change", function () {
        let countryId = $("#country").val();
        rpc("/get-state-data", { country_id: countryId }).then((result) => {
            if (result.status) {
                let text;
                result.state_names.map((e, i) => {
                    text += `<option value="${result.state_ids[i]}-${e}">${e}</option>`;
               });
               $("#state").empty().append(text);
            }
        });
    })
});



