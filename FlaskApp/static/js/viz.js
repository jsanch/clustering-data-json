server_address = 'http://localhost:5000';
url = 'https://data.commerce.gov/data.json';
noaa = 'https://data.noaa.gov/data.json'
k = 10;
function draw_cluster (url,k) {
    server_request = server_address + '/cluster?url=' + url + '&k=' + k
    test_address = 'test-files/testcluster.json'
    // Plotly.d3.json(server_request,function(err,rows){
    width = $(window).width()
    height = $(window).height()
    Plotly.d3.json(test_address,function(err,rows){
        var data = _.chain(rows)
                .groupBy('cluster')
                .map(function(value,key) {
                    return {
                        // name: key,
                        alldata: value,
                        mode: "markers",
                        text: _.pluck(value,'title'),
                        x: _.pluck(value, 'x'),
                        y: _.pluck(value, 'y'),
                        name: value[0].keywords,
                        marker: {size: 12}
                    }
                }).value();
        var layout = {
              "autosize": true,
              "title": "Similarity based on dataset titles and descriptions, clustering using K-Means ",
              "yaxis": {
                "range": [ -0.8598094217567452, 0.8799426613567454 ],
                "type": "linear",
                "autorange": false,
                "showticklabels": false,
                "showgrid": false,
                "zeroline": false
              },
              "height":  width * .95 /2,
              "width": width * .95,
              "xaxis": {
                "range": [ -0.8829826980742848, 0.8156889854742848 ],
                "type": "linear",
                "autorange": true,
                "showticklabels": false,
                "showgrid": false,
                "zeroline": false
              }
            }

        Plotly.newPlot('myDiv', data, layout, {displaylogo: false,scrollZoom: true} );
        // restyle all traces using attribute strings
        // var update = {
        //     'opacity': 1,
        //     'marker.color': 'red',
        // };
        // Plotly.restyle('myDiv', update,2);

        get_tables(k);

    });
}

function get_tables (k) {
    url = 'http://localhost:5000/tables?k='+k;
    d3.json(url, function(error, json) {
        tables = json
        headers = [];

        d3.select("#tables")
          .selectAll("div")
          .data(tables)
          .enter()
          .append("div")
          .attr('class','table-wrapper col-sm-4 centered')
          .append("div")
          .attr('class','tableheader')
          .text(function(d) {
                keywords = $(d).find('th').contents()[0]
                return keywords.data;
            } )

        for (var i = tables.length - 1; i >= 0; i--) {
            // d3.select(tables[i])
        };
        deb = tables;
        d3.selectAll(".table-wrapper")
          .data(tables)
          .append("div")
          .attr('class','cluster-table')
          // .style('height',100)
          // .attr('overflow-y','scroll')
          .html(function(d) {
                return d;
            } )
            d3.selectAll('thead').remove()
    })
}


draw_cluster(noaa,k);