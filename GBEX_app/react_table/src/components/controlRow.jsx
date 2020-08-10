//@flow
"use strict";

import React from 'react'
import {Button, ButtonGroup, ButtonToolbar, Glyphicon, Modal, Form, FormGroup, FormControl, HelpBlock, Grid, Row, Col} from 'react-bootstrap'
import SearchControl from './searchControl'

const scolstyle = {"borderLeft":"1px solid black"}

type State = {
  showModal: boolean,
  currentColName: string,
  form_text: string,
  bulk_text_field: string,
  updatelink: string
}

type Props = {
  columnVisible: Array<string>,
  rowsSelected: Set<string>,
  rowsFoundSorted: Array<string>,
  columnFilter: Set<string>,
  toggleVisibleCols: Function,
  setSearchHighlight: Function,
  clearSearch: Function,
  doFilterClear: Function,
  doSelectFound: Function,
  onEditSuccess: Function,
  scrollToExtreme: Function
}

function createMarkup(value) {
  return {__html: value};
}

export default class ControlRow extends React.PureComponent<Props, State> {
  state = {
    showModal: false,     // show bulk update modal
    currentColName: "",   // column name used for col visibility and bulk update
    form_text: "",        // thex text of bulk update form
    bulk_text_field: "",  // the user entered text field text
    updatelink: ""        // the bulk update update link
  }

  getValidationState() {
    if (this.state.bulk_text_field.split('\n').length == (this.state.form_text.match(/form-group/g) || []).length) return 'success';
    else return 'error';
  }

  handleBulkTextFieldChange = (e: SyntheticKeyboardEvent<FormControl>) => {
    this.setState({ bulk_text_field: e.currentTarget.value });
  }

  close = () => {
    this.setState({ showModal: false });
  }

  open = (e: SyntheticMouseEvent<HTMLUListElement>) => {
    let colname = e.currentTarget.dataset.colname
    let updatelink = window.location.href + "bulkupdate/" + colname + "/" + Array.from(this.props.rowsSelected).join(",")
    this.setState({updatelink: updatelink})
    fetch(updatelink, {credentials: 'include'})
      .then(response => response.text())
      .then(form_text => this.setState({form_text: form_text}))
      .catch(error => console.log(error))
    this.setState({ showModal: true, currentColName: colname });
  }

  handleSubmit = (e: SyntheticEvent<Form>) => {
    fetch(this.state.updatelink, {
      method: 'post',
      credentials: 'include',
      body: new FormData(e.currentTarget)})
      .then(response => {
        let contentType = response.headers.get("content-type");
        if(contentType && contentType.indexOf("application/json") !== -1) {
          return response.json().then(data => {
            this.setState({bulk_text_field: ""})
            this.close()
            this.props.onEditSuccess(this.state.currentColName, data['new_values'])
          });
        } else {
          return response.text().then(text => {
            this.setState({form_text: text})
          });
        }
      }).catch(error => console.log(error));
    e.preventDefault();
  }

  downloadExcel = (ids: Array=[]) => {
    let myheaders = new Headers()
    myheaders.append("X-CSRFToken", window.csrftoken)
    myheaders.append("Accept", "application/json, */*")
    myheaders.append("Content-Type", "application/json")
    fetch(
        window.export_excel_url, {
          method: 'post',
          credentials: 'include',
          headers: myheaders,
          body: JSON.stringify({rids: ids})
        }).then(response => response.blob())
        .then(blob => {
          let url = window.URL.createObjectURL(blob);
          let a = document.createElement('a');
          a.href = url;
          a.download = "export.xlsx";
          document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
          a.click();
          a.remove();  //afterwards we remove the element again
        }).catch(error => console.log(error));
  }

  render() {
    const noneselected = this.props.rowsSelected.size==0  // track whether buttons which deal with selection should be enabled
    let bulk_edit_classs = "btn btn-info btn-sm dropdown-toggle"
    if (noneselected) { bulk_edit_classs += " disabled" }
    const equallines = this.state.bulk_text_field.split('\n').length!=(this.state.form_text.match(/form-group/g) || []).length

    return (
      <div id="toolbar">
        <div id="toolbarleft">
          <SearchControl scrollToExtreme={this.props.scrollToExtreme} rowsFoundSorted={this.props.rowsFoundSorted} columnFilter={this.props.columnFilter} setSearchHighlight={this.props.setSearchHighlight} doFilterClear={this.props.doFilterClear} doSearchClear={this.props.clearSearch} doSelectFound={this.props.doSelectFound} />
        </div>
        <div id="toolbarright">
          <ButtonToolbar>
            <ButtonGroup>
              <Button bsSize="sm" bsStyle="primary" onClick={() => window.location.href = window.createurl}>Add rows <Glyphicon glyph="plus" /></Button>
              <Button bsSize="sm" bsStyle="primary" disabled={noneselected} onClick={() => window.location.href = window.location.href + "archive/" + Array.from(this.props.rowsSelected).join(",")}>Archive rows <Glyphicon glyph="minus" /></Button>
              <Button bsSize="sm" bsStyle="primary" onClick={() => window.location.href = window.location.href + "bulkupload/"}>Bulk upload <Glyphicon glyph="cloud-upload" /></Button>
            </ButtonGroup>
            <ButtonGroup>
              <button type="button" className={bulk_edit_classs} data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Edit all selected <span className="caret"></span></button>
              <ul className="dropdown-menu">{window.columns.slice(2).map(v => <li key={v}><a onClick={this.open} data-colname={v} >{v}</a></li>)}</ul>
            </ButtonGroup>
            <ButtonGroup>
              <button type="button" className="btn btn-info btn-sm btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Show/hide columns <span className="caret"></span></button>
              <ul className="dropdown-menu">{window.columns.slice(2).map(v => <li key={v}><a onClick={this.props.toggleVisibleCols} data-column={v}>{this.props.columnVisible.includes(v) ? "hide " : "show "}{v}</a></li>)}</ul>
            </ButtonGroup>
            <ButtonGroup>
              <Button bsSize="sm" bsStyle="primary" onClick={() => this.downloadExcel()}>Download table <Glyphicon glyph="cloud-download" /></Button>
              <Button bsSize="sm" bsStyle="primary" disabled={noneselected} onClick={() => this.downloadExcel(Array.from(this.props.rowsSelected))}>Download selected <Glyphicon glyph="cloud-download" /></Button>
            </ButtonGroup>
          </ButtonToolbar>
        </div>

        <Modal bsSize="large" show={this.state.showModal} onHide={this.close}>
          <Modal.Header closeButton>
            <Modal.Title>Bulk edit {this.state.currentColName}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Grid fluid={true}>
              <Row>
                <Col md={6}>
                  Copy+Paste here. One line per field on right. If multi-select fields, then comma seperate.
                  <FormGroup controlId="formBasicText" validationState={this.getValidationState()}>
                    <FormControl name="allforone" componentClass="textarea" rows={(this.state.form_text.match(/form-group/g) || []).length} cols="20" value={this.state.bulk_text_field} placeholder="Enter text" onChange={this.handleBulkTextFieldChange} />
                    <FormControl.Feedback />
                    <HelpBlock>The number of lines has to match the number of fields on the right ({this.state.bulk_text_field.split('\n').length}/{(this.state.form_text.match(/form-group/g) || []).length})</HelpBlock>
                  </FormGroup>
                  <Button onClick={window.bulk_text_apply} bsStyle="primary" disabled={equallines}>Copy text to fields on right</Button>
                </Col>
                <Col md={6} style={scolstyle}>
                  <Form id="bulk_form_set_form" horizontal onSubmit={this.handleSubmit}>
                    <div dangerouslySetInnerHTML={createMarkup(this.state.form_text)} />
                    <FormGroup>
                      <Col mdOffset={6} md={6}>
                        <Button block onClick={() => window.allforone(this.props.rowsSelected.size)}>All equal top field</Button>
                        <Button type="submit" block bsStyle="primary">Submit<span className="glyphicon glyphicon-save" /></Button>
                      </Col>
                    </FormGroup>
                  </Form>
                </Col>
              </Row>
            </Grid>
          </Modal.Body>
        </Modal>
      </div>
    )
  }
}
