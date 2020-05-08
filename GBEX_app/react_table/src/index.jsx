//@flow
"use strict";

import React from 'react';
import ReactDOM from 'react-dom'
import GBEXtable from './components/GBEXtable'
import './css/mytable.css'

/*
window.table_settings is a json object

{
  'table_name_1': {
    'window.column_widths': {
      'column_name_1': number,
      'column_name_2': number,
      etc
    },
    'window.column_shows': [
      'column_name_1',
      'column_name_2',
      etc
    ]
  },
  'table_name_2': etc,
}

*/

// see if have table settings for this table
if (!window.table_settings.hasOwnProperty(window.whodis)) { // if not, make an empty dict
  window.table_settings[window.whodis] = {}
}
// see if we have column widhts
if (!window.table_settings[window.whodis].hasOwnProperty(window.column_widths)) {
  window.table_settings[window.whodis][window.column_widths] = Object.assign({}, ...window.columns.map(d => ({[d]: d.length*12+50}))) //default widhts based on name length
} else {
  // go over to remove obsolete widths
  let myWidths = Object.assign({}, ...window.columns.map((d, i) => {
    if (window.table_settings[window.whodis][window.column_widths].hasOwnProperty(d)) {
      return {[d]: window.table_settings[window.whodis][window.column_widths][d]}
    } else {
      return {[d]: d.length*15}
    }
  }))
  window.table_settings[window.whodis][window.column_widths] = {...myWidths}
}
// see if we have visible columns
if (!window.table_settings[window.whodis].hasOwnProperty(window.column_shows)) {
  window.table_settings[window.whodis][window.column_shows] = [...window.columns] //default show all
} else {
  // go through to remove obsolete columns
  window.table_settings[window.whodis][window.column_shows] = [...window.columns.filter(d => window.table_settings[window.whodis][window.column_shows].includes(d))]
}

ReactDOM.render(
  <GBEXtable
    InitialColumnWidths={window.table_settings[window.whodis][window.column_widths]}
    InitialColumnVisible={window.table_settings[window.whodis][window.column_shows]} />,
  document.getElementById('root')
);
