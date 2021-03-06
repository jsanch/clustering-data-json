deb =''
server_address = 'http://localhost:5000';
url = 'https://data.commerce.gov/data.json';
noaa = 'https://data.noaa.gov/data.json'
k = 10;
function draw_cluster (url,k) {
    server_request = server_address + '/cluster?url=' + url + '&k=' + k
    test_address = 'test-files/testcluster.json'
    width = $(window).width()
    height = $(window).height()
    Plotly.d3.json(server_request,function(err,json){
    // Plotly.d3.json(test_address,function(err,json){
        var rows = $.parseJSON(json[0]);

        var metadata = json[1];

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
        // console.log(data);
        Plotly.newPlot('myDiv', data, layout, {displaylogo: false,scrollZoom: true} );

        deb = data;
        console.log(data);
        get_tables(data,k);
    d3.select('#cluster-info').append('h4').text('Understanding the visualization')
    d3.select('#cluster-info').append('p').text('The visualization at the top of the page is a 2-dimensional scatterplot of the cosine distance of each of the portal\'s datasets (colored by cluster). The dimensions (X and Y) do not actually have labels. The way to interpret the the scatterplot is by examining the location of one dataset, relative to others, in this 2-d space. Proximity in this space equates to similarity as determined by a multi-dimensional scaling of the cosine distance (1 minus cosine similarity) between the title and descriptions of a dataset contained within the term frequency-inverse document frequency (tf-idf) matrix. That was probably confusing and I plan to explain it in a more detailed write up of my methodology, but the basic intuition is that, based on the collected  medatada, each dataset is plotted in relation to its similarity to all other datasets contained in the plot. You might find some wierd relationships in this plot: keep in mind that similarity was measured based on the words found in the dataset titles and descriptions. If the metadata was written poorly or very short the results were most certainly impacted. Garbage in, garbage out. Mostly I was interested in exploring the methodology (Machine learning and K-means clustering).')
    d3.select('#cluster-info').append('h5').text('Analyzed url: ' + url)
    d3.select('#cluster-info').append('h5').text('k :' + k)
    d3.select('#cluster-info').append('h5').text('Number of datasets: ' + rows.length)
    d3.select('#cluster-info').append('a').attr('href',"static/cluster_data.csv").text('Download Underlying data')

    });
}

function get_tables (data,k) {
        headers = [];
        console.log(data)
        //get colors from legend
        tempkeys = d3.select(".legend").selectAll(".legendtext")[0];
        tempcolors = d3.select(".legend").selectAll(".scatterpts")[0];
        keyword_dict= {};
        for (var i = 0; i <= tempkeys.length - 1; i++) {
            keyword_dict[tempkeys[i].textContent] = tempcolors[i].style.fill;
        };
        keyword_list = []
        for (var key in keyword_dict){
            keyword_list.push(key)
        }

        console.log(keyword_list);
        d3.select("#tables")
          .selectAll('div')
          .data(keyword_list)
          .enter()
          .append("div")
          .attr('class','table-wrapper col-md-4')
          .append("div")
          .attr('class','tableheader')
          .text(function(d) {
                return d
            } );

        d3.selectAll(".table-wrapper")
          .data(data)
          .append("div")
          .attr('class','cluster-table')
          .html(function(d) {
                    tbody = "<tbody>"
                    tr = "<tr>"
                    _tr = "</tr>"
                    td = "<td>"
                    _td = "</td>"
                    var tmp = "<table border=\"1\" class=\"dataframe\">" + tbody
                for (var i = d.alldata.length - 1; i >= 0; i--) {
                    tmp = tmp + tr + td + d.alldata[i].title + _td + _tr;
                    // console.log(tmp);
                };
                    total = tmp + tr + td + "TOTAL: "+ d.alldata.length + _td + _tr + "</tbody>";
                return total;
            } )
            d3.selectAll('thead').remove()
        //  color headeers
        headers = d3.selectAll(".tableheader")[0]
        for (var i = 0; i <= headers.length - 1; i++) {
            var color = 'rgba'+ keyword_dict[headers[i].textContent].slice(3,-1) + ', 0.5)'
            headers[i].style.backgroundColor = color;
        };
    // })
}

function clear_all () {
    console.log("clearing..")
    d3.selectAll('.table-wrapper').remove()

    // d3.selectAll('.table-wrapper').selectAll('.cluster-table').remove()
    d3.select('#cluster-info').selectAll('h4').remove()
    d3.select('#cluster-info').selectAll('p').remove()
    d3.select('#cluster-info').selectAll('h5').remove()
    d3.select('#cluster-info').selectAll('a').remove()
}

$('#vizbtn').on('click', function () {
    clear_all();

    var k = document.getElementById('k').value
    var url = document.getElementById('data_json_url').value
    draw_cluster(url,k);
})

// draw_cluster(url,k);
