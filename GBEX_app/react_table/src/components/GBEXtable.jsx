//@flow
"use strict";

import React from 'react';
import ControlRow from './controlRow'
import RVMultiGrid from './multiGrid'

function checkEachColumn(searchColumns: Object, currentRow: Array<string>): boolean {
  return Object.entries(searchColumns).every(([columnName, columnSearchString]) => { // check if every search column string passes
    if (!columnSearchString) { return true } // no text is automatic pass
    let colIndex = window.columns.indexOf(columnName)
    let cc = currentRow[colIndex].toString().toLowerCase();
    // if there are &, | or ! then do boolean, otherwise normal string search
    if (columnSearchString.includes("&") || columnSearchString.includes("!") || columnSearchString.includes("|")) {
      try {
        return eval(columnSearchString.toLowerCase().replace(/([^&|! ]+)/g, "(cc.search('$1')>=0)"))
      } catch (e) { return false }
    } else {
      return columnSearchString.toLowerCase().split(" ").every(word => cc.includes(word))
    }
  })
}

function sortByColumn(sortDirection: string, sortColumn: number, data: Array<Array<any>>) {
  const comparer = (a, b) => {
    let first = a[sortColumn];
    let second = b[sortColumn];
    if (sortDirection === 'DESC') {
      first = b[sortColumn];
      second = a[sortColumn];
    }
    if (sortColumn === 1) { // special case for name column, sort by the number that all names have...not very generic, but this project is deprecated so I don't care
      // try to get a number of the end of the string, but if none exist, then just use the id columns
      let noone = first.match(/[0-9]+$/);
      let notwo = second.match(/[0-9]+$/);
      if (Array.isArray(noone) && Array.isArray(notwo)) {
        first = parseInt(noone[0]);
        second = parseInt(notwo[0]);
      } else if (sortDirection === "DESC") {
        first = b[0];
        second = a[0];
      } else {
        first = a[0];
        second = b[0];
      }
    }

    if (first < second) {
      return -1
    } else if (first > second) {
      return 1
    } else {
      return a[0]-b[0] // in case of tie, let id column determine
    }
  }

  return data.slice().sort(comparer)
}

function search(searchColumns: Object, data: Array<Array<string>>) {
  if (Object.values(searchColumns).join('')) { // if any search string
    // find rows that match the search criteria and take the id from those rows
    return data.filter(d => checkEachColumn(searchColumns, d)).map(d => d[0].toString())
  }
  return []
}

type Props = {
  InitialColumnWidths: Object,          // initial column widths {'name': number, }
  InitialColumnVisible: Array<string>,  // columns that are visible
}

type State = {
  data: Array<Array<string>>,
  filtered_sorted_data: Array<Array<string>>,
  rowsSelected: Set<string>,
  rowsFoundSorted: Array<string>,
  columnVisible: Array<string>,
  columnWidths: Object,
  columnSortDir: string,
  columnSortCol: number,
  columnSearch: Object,
  columnFilter: Set<string>,
  searchCursor: string,
}

export default class GBEXtable extends React.PureComponent<Props, State> {
  state = {
    data: window.data.slice(),                                      // all the data, this will be updated on succesful submits
    filtered_sorted_data: sortByColumn("ASC", 1, window.data.slice()), // this is the filtered sorted data which will be updated on filter/sort commands
    rowsSelected: new Set(),                                        // currently manually selected rows (ids not row index)
    rowsFoundSorted: [],                                           // rows matching search fields
    columnVisible: this.props.InitialColumnVisible.slice(),         // ordered list of visible columns
    columnWidths: {...this.props.InitialColumnWidths},              // width of columns
    columnSortDir: "ASC",                                          // column sort direction ASC, DESC
    columnSortCol: 1,                                               // column index used for sorting
    columnSearch: Object.assign({}, ...window.columns.map(d => {return {[d]: ""}})), // column search field contents
    columnFilter: new Set(),																				// column filter fields contents
    searchCursor: "",                                               // currently highlighted search result
  };

  rvmg: RVMultiGrid;

  // used to hide/show cols
  _toggleVisibleCols = (e: SyntheticMouseEvent<HTMLAnchorElement>) => {
    let colname = e.currentTarget.dataset.column;
    let ncols = this.state.columnVisible.slice();
    // is this column shown?
    if (this.state.columnVisible.includes(colname)) { //yes its visible
      // so hide it
      ncols.splice(ncols.indexOf(colname), 1)
    } else { // no its not visible
      // figure out where to insert this
      let colindexes = ncols.map(d => window.columns.indexOf(d));
      colindexes.push(window.columns.indexOf(colname));
      ncols = colindexes.sort((a, b) => a - b).map(d => window.columns[d])
    }

    this.setState({columnVisible: ncols}, this._commitTableSettings)
  };

  _doColumnResize = (target_name: string, new_col_width: number) => {
    new_col_width = this.state.columnWidths[target_name] + new_col_width;
    if (new_col_width < 50) {
      new_col_width = 50
    }

    this.setState({columnWidths: {...this.state.columnWidths, [target_name]: new_col_width}}, () => {this._commitTableSettings(); this.rvmg.mugi.recomputeGridSize(); this.rvmg.mugi.forceUpdate();})
    this.rvmg.setState({dragCurrentX: -10, scrollToColumn: -1, editActive: false})
  };

  _onRowSelectChange = (e: SyntheticEvent<HTMLInputElement>) => {
    let new_rows_selected = new Set(this.state.rowsSelected)
    if (e.currentTarget.checked) {
      new_rows_selected.add(e.currentTarget.name)
    } else {
      new_rows_selected.delete(e.currentTarget.name)
    }
    this.setState({rowsSelected: new_rows_selected})
    this.rvmg.mugi.forceUpdateGrids()
  }

  _onRowSelectToggleAll = (e: SyntheticEvent<HTMLInputElement>) => {
    if (this.state.rowsSelected.size == this.state.filtered_sorted_data.length) { // everything selected so deselect all
      this.setState({rowsSelected: new Set()})
    } else { // not everything is selected so do that
      this.setState({rowsSelected: new Set(this.state.filtered_sorted_data.map(d => d[0].toString()))})
    }
    this.rvmg.mugi.forceUpdateGrids()
  }

  _doFilter = (e: SyntheticEvent<HTMLButtonElement>) => {
    let ncf = new Set(this.state.columnFilter)
    if (e.currentTarget.checked) { ncf.add(e.currentTarget.dataset.name) } else { ncf.delete(e.currentTarget.dataset.name) }
    this.setState({columnFilter: ncf}, this._dodoFilter)
  }

  _doSearch = (e: SyntheticEvent<HTMLButtonElement>) => {
    let new_column_search = {...this.state.columnSearch, [e.currentTarget.dataset.name]: e.currentTarget.value}
    this.setState({columnSearch: new_column_search}, this._dodoFilter);
  }

    //updates filtered_sorted_data and rowsFound
  _dodoFilter = () => {
    let filtercolumns = Object.assign({}, ...Array.from(this.state.columnFilter).map(d => {return {[d]: this.state.columnSearch[d]}}))
    let fdata = this.state.data.filter(d => checkEachColumn(filtercolumns, d))
    //then call sort
    let sfdata = sortByColumn(this.state.columnSortDir, this.state.columnSortCol, fdata)
    //then call search
    let searchcolumns = Object.assign({}, ...Object.keys(this.state.columnSearch).map(d => {
      if (!this.state.columnFilter.has(d)) {
        return {[d]: this.state.columnSearch[d]}
      }}
    ))

    this.setState({filtered_sorted_data: sfdata, rowsFoundSorted: search(searchcolumns, sfdata)}, () => {
      this.rvmg.mugi.forceUpdate(); this.rvmg.mugi.forceUpdateGrids();
    })
  }

  _doSort = (e: SyntheticEvent<HTMLButtonElement>) => {
    let sortColumn = window.columns.indexOf(e.currentTarget.dataset.name)
    let sortDirection = "ASC"
    if (this.state.columnSortDir == "ASC") {
      sortDirection = "DESC"
    }

    this.setState({columnSortDir: sortDirection, columnSortCol: sortColumn, filtered_sorted_data: sortByColumn(sortDirection, sortColumn, this.state.filtered_sorted_data)})
    this.rvmg.mugi.forceUpdateGrids()
  }

  // inline editor commits
  _onCommit = (new_value: Object, colname: string, id: string) => {
    window.killSelect2();
    this._onEditSuccess(colname, {[id]: new_value['new_value']})
    this.rvmg.setState({editActive: false})
    this.rvmg.aks.focus()
  }

  //bulk editor
  _onEditSuccess = (column_name: string, new_values: Object) => {
    let tcolumnIndex = window.columns.indexOf(column_name)
    let new_data = this.state.data.slice()
    Object.entries(new_values).forEach(([key, value]) => {
      let row_index = this.state.data.findIndex(d => d[0] == key)
      let new_row = this.state.data[row_index].slice()
      new_row.splice(tcolumnIndex, 1, value)
      new_data.splice(row_index, 1, new_row)
    })
    this.setState({data: new_data}, this._dodoFilter)
  }

  _commitTableSettings = () => {
    window.table_settings[window.whodis][window.column_widths] = {...this.state.columnWidths}
    window.table_settings[window.whodis][window.column_shows] = this.state.columnVisible.slice()
    let myheaders = new Headers()
    myheaders.append("X-CSRFToken", window.csrftoken)
    myheaders.append("Accept", "application/json, */*")
    myheaders.append("Content-Type", "application/json")
    fetch(`/api/Profile/${window.settings_id}/`, {
      method: 'put', credentials: 'include', headers: myheaders,
      body: JSON.stringify(
        {
          "user": window.user_id,
          "table_settings": JSON.stringify(window.table_settings)
        })}).catch(error => console.log(error))
  }

  _clearSearch = () => {
    let clearsearchcolumns = Object.assign({}, ...Object.entries(this.state.columnSearch).map(([k, v]) => {
      if (!this.state.columnFilter.has(k)) { return {[k]: ""} } else {return {[k]: v}}}
    ))
    this.setState({columnSearch: clearsearchcolumns}, this._dodoFilter)
  }

  _doFilterClear = () => {
    this.setState({columnFilter: new Set()}, this._dodoFilter)
  }

  _doSelectFound = () => {
    this.setState({rowsSelected: new Set([...this.state.rowsSelected, ...this.state.rowsFoundSorted])})
    this.rvmg.mugi.forceUpdateGrids()
  }

  _setSearchHighlight = (row_id: string) => {
    this.setState({searchCursor: row_id})
    // find row index
    let scrollTo = this.state.filtered_sorted_data.findIndex(d => d[0].toString() == row_id) + 1
    // over/under scroll
    if (scrollTo > this.rvmg.state.scrollToRow) {
      if (scrollTo < this.state.filtered_sorted_data.length - 5) {
        scrollTo += 5
      }
    } else {
      if (scrollTo > 5) {
        scrollTo -= 5
      }
    }

    this.rvmg.setState({scrollToRow: scrollTo}, this.rvmg.mugi.forceUpdateGrids())
  }

  _scrollToExtreme = (scroll_to_start: boolean) => {
    let col_number = 1
    if (!scroll_to_start) {
      col_number = this.state.filtered_sorted_data.length
    }
    this.rvmg.setState({scrollToRow: col_number})
  }

  render() {
    return (
      <div id="GBEXtable_root">
        <ControlRow
          columnVisible={this.state.columnVisible}
          rowsSelected={this.state.rowsSelected}
          rowsFoundSorted={this.state.rowsFoundSorted}
          toggleVisibleCols={this._toggleVisibleCols}
          columnFilter={this.state.columnFilter}
          setSearchHighlight={this._setSearchHighlight}
          clearSearch={this._clearSearch}
          doFilterClear={this._doFilterClear}
          onEditSuccess={this._onEditSuccess}
          doSelectFound={this._doSelectFound}
          scrollToExtreme={this._scrollToExtreme}
        />
        <RVMultiGrid
          ref={el => this.rvmg = el}
          columnVisible={this.state.columnVisible}
          columnWidths={this.state.columnWidths}
          columnSearch={this.state.columnSearch}
          columnFilter={this.state.columnFilter}
          rowsSelected={this.state.rowsSelected}
          rowsFoundSorted={this.state.rowsFoundSorted}
          searchCursor={this.state.searchCursor}
          data={this.state.filtered_sorted_data}
          doColumnResize={this._doColumnResize}
          onRowSelectChange={this._onRowSelectChange}
          onRowSelectToggleAll={this._onRowSelectToggleAll}
          doFilter={this._doFilter}
          doSearch={this._doSearch}
          doSort={this._doSort}
          doCommit={this._onCommit}
        />
      </div>
    )
  }
}
