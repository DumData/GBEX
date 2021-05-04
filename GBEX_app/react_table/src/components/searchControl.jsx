//@flow
"use strict";

import React from 'react'
import { PureComponent } from 'react';
import {Button, Glyphicon, ButtonGroup, ButtonToolbar } from 'react-bootstrap'

function arraysEqual(a, b) {
  if (a === b) return true;
  if (a == null || b == null) return false;
  if (a.length != b.length) return false;

  for (var i = 0; i < a.length; ++i) {
    if (a[i] !== b[i]) return false;
  }
  return true;
}

type State = {
  rowSearchHighlightIndex: number,
}

type Props = {
  rowsFoundSorted: Array<string>,
  columnFilter: Set<string>,
  setSearchHighlight: Function,
  doSearchClear: Function,
  doFilterClear: Function,
  doSelectFound: Function,
  scrollToExtreme: Function
}

export default class SearchControl extends PureComponent<Props, State> {
  state = {
    rowSearchHighlightIndex: 0
  }

  componentWillReceiveProps(nextProps: Object) {
    if (!arraysEqual(this.props.rowsFoundSorted, nextProps.rowsFoundSorted)) {
      // something changed in the found rows
      if (nextProps.rowsFoundSorted.length == 0) {
        this.setState({rowSearchHighlightIndex: 0})
        this.props.setSearchHighlight("none")
      } else {
        // lets see if currently selected row still exist
        let current_id = this.props.rowsFoundSorted[this.state.rowSearchHighlightIndex]
        let new_index = nextProps.rowsFoundSorted.indexOf(current_id)
        if (new_index == -1) { // previous index dont exist anymore...lets just reset
          this.setState({rowSearchHighlightIndex: 0})
          this.props.setSearchHighlight(nextProps.rowsFoundSorted[0])
        } else { // row is still in found list, but it has a new index
          this.setState({rowSearchHighlightIndex: new_index})
        }
      }
    }

    /*else if (this.state.rowSearchHighlightIndex > nextProps.rowsFoundSorted.length - 1) {
      this.setState({rowSearchHighlightIndex: nextProps.rowsFoundSorted.length - 1})
      this.props.setSearchHighlight(nextProps.rowsFoundSorted.slice(-1)[0])
    }*/

  }

  _doSearchSelectLeft = () => {
    let nrshi = this.props.rowsFoundSorted.length - 1
    if (this.state.rowSearchHighlightIndex > 0) {
      nrshi = this.state.rowSearchHighlightIndex - 1
    }
    this.setState({rowSearchHighlightIndex: nrshi })
    this.props.setSearchHighlight(this.props.rowsFoundSorted[nrshi])
  }

  _doSearchSelectRight = () => {
    let nrshi = 0
    if (this.state.rowSearchHighlightIndex < this.props.rowsFoundSorted.length - 1) {
      nrshi = this.state.rowSearchHighlightIndex + 1
    }
    this.setState({rowSearchHighlightIndex: nrshi})
    this.props.setSearchHighlight(this.props.rowsFoundSorted[nrshi])
  }

  render() {
    const noresults = this.props.rowsFoundSorted.length == 0
    const nofilters = this.props.columnFilter.size == 0
    return (
      <div>
        <ButtonToolbar>
          <ButtonGroup bsSize="sm">
            <Button bsStyle="primary" onClick={() => this.props.scrollToExtreme(true)}><Glyphicon glyph="step-backward" style={{transform: "rotate(90deg)"}}/></Button>
            <Button bsStyle="primary" onClick={() => this.props.scrollToExtreme(false)}><Glyphicon glyph="step-forward" style={{transform: "rotate(90deg)"}}/></Button>
          </ButtonGroup>

          <ButtonGroup bsSize="sm" >
            <Button bsStyle="primary" disabled={noresults} onClick={this._doSearchSelectLeft}><Glyphicon glyph="chevron-left"/></Button>
            <Button bsStyle="success" disabled>{this.props.rowsFoundSorted.length == 0 ? 0 : this.state.rowSearchHighlightIndex + 1} / {this.props.rowsFoundSorted.length}</Button>
            <Button bsStyle="primary" disabled={noresults} onClick={this._doSearchSelectRight}><Glyphicon glyph="chevron-right"/></Button>
          </ButtonGroup>

          <ButtonGroup bsSize="sm" >
            <Button bsStyle="info" onClick={this.props.doSearchClear}>Clear Search <Glyphicon glyph="remove" /></Button>
            <Button bsStyle="info" disabled={nofilters} onClick={this.props.doFilterClear}>Clear Filter <Glyphicon glyph="remove" /></Button>
            <Button bsStyle="info" disabled={noresults} onClick={this.props.doSelectFound}>Select found <Glyphicon glyph="ok" /></Button>
          </ButtonGroup>
        </ButtonToolbar>
      </div>
    )
  }
}
