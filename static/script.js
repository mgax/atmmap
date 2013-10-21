(function() {
    "use strict";

    var app = window.app;

    app.brands_select = $('#menu [name=brands]').select2({
        data: _.map(app.brands, function(code) {
            return {id: code, text: code};
        }),
        multiple: true,
        allowClear: true,
        width: '180px'
    });
    app.brands_select.on('change', function(e) {
        update_markers();
    });

    app.selected_brands = [];
    function update_markers() {
        app.selected_brands = app.brands_select.select2('val');
        render_markers();
    }


    var attribution = '&copy; <a href="http://osm.org/copyright">'
                    + 'OpenStreetMap</a> contributors';
    app.map = L.map('map').setView([app.center.lat, app.center.lon], 12);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
            attribution: attribution
    }).addTo(app.map);

    if(app.draw_bbox) {
        var bounds = [[app.bbox.S, app.bbox.W], [app.bbox.N, app.bbox.E]];
        L.rectangle(bounds, {color: "#ff7800", weight: 1}).addTo(app.map);
    }

    var data = [];
    app.markers = new L.LayerGroup();
    app.markers.addTo(app.map);

    $.getJSON(app.data_url, function(resp_data) {
        data = resp_data;
        render_markers();
    });

    function render_markers() {
        app.markers.clearLayers();
        _(data).forEach(function(item) {
            if(app.selected_brands.length > 0) {
                if(_.indexOf(app.selected_brands, item['brand']) == -1) {
                    return;
                }
            }
            var marker = L.marker([item['lat'], item['lon']]);
            marker.addTo(app.markers);
            marker.bindPopup(item['brand'] || "");
        });
    }
})();
