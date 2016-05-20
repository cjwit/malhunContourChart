var data;

var margin = { top: 20, right: 20, bottom: 30, left: 30},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var x = d3.scale.linear()
    .range([0, width]);

var y = d3.scale.linear()
    .range([height, 0]);

var color = d3.scale.category10();

var xAxis = d3.svg.axis()
    .scale(x)
    .orient('bottom')

var yAxis = d3.svg.axis()
    .scale(y)
    .orient('left')

var line = d3.svg.line()
    .interpolate('linear')
    .x(function(d) { return x(d.offset); })
    .y(function(d) { return y(d.frequency); })

var chart = d3.select('.chart')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
  .append('g')
    .attr('class', 'container')
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

// buttons
var titleArtist = [];
var selected = [];
var setListeners = function() {
    $('.selector').click(function(e) {
        e.preventDefault();
        var title = e.target.id;
        var index = selected.indexOf(title)
        if (index === -1) {
            selected.push(title);
        } else {
            selected.splice(index, 1)
        }

        if (selected.length === 0) {
            $('.melody').each(function(index) {
                $(this).css('opacity', '');
            })
        } else {
            $('.melody').each(function(index) {
                var melodyID = $(this).attr('id').replace(':', ': ');
                if (selected.indexOf(melodyID) !== -1) {
                    $(this).css('opacity', '.9')
                } else {
                    $(this).css ('opacity', '.1')}
            });
        }
    });
}

var createButtons = function() {
    var buttons = $('#buttons');
    buttons.addClass('btn-group');
    buttons.attr('data-toggle', 'buttons');
    titleArtist.map(function(title, index) {
        var label = $('<label></label>')
            .addClass('btn btn-default')
            .attr('id', title)
            .addClass('selector');
        var button = $('<input/>')
            .attr('type', 'checkbox')
            .attr('autocomplete', 'off');
        label.append(button).append(title);
        buttons.append(label);
    });
    setListeners();
}

var filterData = function(data) {
    data = data.filter(function(melody) {
        if (selected.length === 0) {
            return true
        }
        melodyID = melody.metadata.title + ": " + melody.metadata.artist;
        return selected.indexOf(melodyID) !== -1;
    })
    return data
}

var formatData = function(data) {
    // set up colors and normalize durations
    data.map(function(m) {
        var domain = m.metadata.title + ': ' + m.metadata.artist;
        if (titleArtist.indexOf(domain) === -1) { titleArtist.push(domain) }

        var pieceLength = m.notes[m.notes.length - 1].duration + m.notes[m.notes.length - 1].offset;
        m.notes.map(function(n) {
        n.offset = n.offset / pieceLength * 100;
        n.duration = n.duration / pieceLength * 100;
        })
    })

    // finish color setup
    var color = d3.scale.category10()
        .domain(titleArtist);

    shortestDuration = d3.min(data, function(d) {
        return (d3.min(d.notes, function(d) { return d.duration }))
    })
    filledIn = []
    var xAxisLength = 100;
    data.map(function(m) {
        var melody = {};
        melody.metadata = m.metadata;
        melody.notes = [];

        // create final note to append later, adjust for final rests
        var lastNote = {
            'duration': m.notes[m.notes.length - 1].duration,
            'offset': m.notes[m.notes.length - 1].duration + m.notes[m.notes.length - 1].offset,
            'frequency': m.notes[m.notes.length - 1].frequency,
            'fromRoot': m.notes[m.notes.length - 1].fromRoot
        }

        if (lastNote.frequency === 'rest') {
            var i = m.notes.length - 1;
            while (m.notes[i].frequency === 'rest') {
                i -= 1;
            }
            lastNote.frequency = m.notes[i].frequency;
            lastNote.fromRoot = m.notes[i].fromRoot;
        }

        m.notes.map(function(n, i) {
            // skip initial rests
            if (melody.notes.length === 1 || n.frequency !== 'rest') {
                melody.notes.push(n);
            }

            // extend lengths to almost meet the next pitch change
            // check that we are not on the last note
            if (i < m.notes.length - 1) {

                // check that this is not a rest that was skipped over
                previous = melody.notes[melody.notes.length - 1];
                var previousOffset = 0;
                if (previous) {
                    previousOffset = previous.offset;
                }
                if (n.offset >= previousOffset) {

                    // create new note object to insert
                    var advance = 1;
                    var next = {
                        'duration': m.notes[i + advance].duration,
                        'offset': m.notes[i + advance].offset - shortestDuration,
                        'frequency': m.notes[i + advance].frequency,
                        'fromRoot': m.notes[i + advance].fromRoot
                    }

                    // if a rest is next, skip ahead
                    while (next.frequency === 'rest') {
                        advance += 1;

                        // in case we skipped to the end
                        if (i + advance >= m.notes.length) {
                            var next = lastNote
                            break;
                        } else {
                            var next = {
                                'duration': m.notes[i + advance].duration,
                                'offset': m.notes[i + advance].offset - shortestDuration,
                                'frequency': n.frequency,
                                'fromRoot': n.fromRoot
                            }
                        }
                    }
                    melody.notes.push(next);

                }
            } else {
                melody.notes.push(lastNote);
            }
        })
        filledIn.push(melody)
    })
    return filledIn;
}

d3.json('malhun.json', function(error, data) {
    if (error) return console.warn(error);

    // build chart
    data = formatData(data);
    x.domain([0, (d3.max(data, function(d) {
        return (d3.max(d.notes, function(d) { return d.offset }))
    }))]);
    y.domain([
        d3.min(data, function(d) {
            return (d3.min(d.notes, function(d) { return d.frequency }))
        }), d3.max(data, function(d) {
            return (d3.max(d.notes, function(d) { return d.frequency }))
        })
    ]);

    // add axes, title
    chart.append('g')
        .attr('class', 'axis axis--x')
        .attr('transform', 'translate(0,' + height + ')')
        .call(xAxis)
      .append('text')
        .attr('x', width - 10)
        .attr('y', -6)
        .attr('dx', '.71em')
        .style('text-anchor', 'end')
        .text('Time (%)')

    chart.append('g')
        .attr('class', 'axis axis--y')
        .call(yAxis)
      .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 6)
        .attr('dy', '.71em')
        .style('text-anchor', 'end')
        .text('Frequency');

    chart.append('g')
        .attr('class', 'title')
      .append('text')
        .attr('y', 20)
        .attr('x', width / 2)
        .style('text-anchor', 'middle')
        .text('Contours of Some Malhun Melodies');

    // visualize data
    var melody = chart.selectAll('.melody')
        .data(data)
      .enter().append('g')
        .attr('class', 'melody')
        .attr('id', function(d) {
            return d.metadata.title + ":" + d.metadata.artist;
        })

    melody.append('path')
        .attr('class', 'line')
        .attr('d', function(d) {
            var values = d.notes.map(function(note, index) {
                return { offset: note.offset, frequency: note.frequency }
            });
            return line(values);
        })
        .attr('id', function(d, i) { return 'path-' + i; })
        .style('stroke', function(d) { return color(d.metadata.title + ": " + d.metadata.artist) })

    melody.append('text')
        .attr('dy', -5)
      .append('textPath')
        .attr('class', 'textpath')
        .attr('startOffset', function(d) {
            var numRefrains = d3.max(data, function (d) { return Number(d.metadata.refrain) });
            var refrain = (Number(d.metadata.refrain) - 1) * 1.0
            return String(refrain / numRefrains * 100.0) + '%';
        })
        .attr('xlink:href', function(d, i) { return '#path-' + i; })
        .text(function(d) { return d.metadata.title + ' (' + d.metadata.artist + '), harba ' + d.metadata.refrain; })

    createButtons();
})
