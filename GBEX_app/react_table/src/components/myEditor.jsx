//@flow
"use strict";

import React from 'react'
import { PureComponent } from 'react';
import { Popover, FormGroup, Button } from 'react-bootstrap'
import { findDOMNode } from 'react-dom'

const form_style = {display: "inline-flex"};

type State = {
  form_text: string,
  updatelink: string
}

type Props = {
  columnName: string,
  pk: string,
  style: Object,
  onCommit: Function,
}

export default class MyEditor extends PureComponent<Props, State> {
  state = {
    form_text: "",
    updatelink: ""
  };

  formb: ?Button;
  formg: ?FormGroup;

  componentDidMount() {
    let updatelink = window.location.href + "update/" + this.props.pk + "/" + this.props.columnName;
    this.setState({updatelink: updatelink});
    fetch(updatelink, {credentials: 'include'})
      .then(response => response.text())
      .then(form_text => {
        //this.setState({form_text: form_text})
        let newdiv = document.createElement('div');
        newdiv.innerHTML = form_text;
        for (let ascrip of newdiv.getElementsByTagName("script")) {
          newdiv.appendChild(ascrip);
        }
        document.getElementById('target').appendChild(newdiv);
        for (let ascrip of newdiv.getElementsByTagName("script")) {
          if (ascrip.innerHTML != "") {
            eval(ascrip.innerHTML)
          }
        }
        newdiv.focus()
      })
      .catch(error => console.log(error))
  }

  handleSubmit = (event: SyntheticEvent<Form>) => {
    fetch(this.state.updatelink, {
      method: 'post',
      credentials: 'include',
      body: new FormData(event.currentTarget)})
      .then(response => response.json())
      .then(thattext => this.props.onCommit(thattext, this.props.columnName, this.props.pk))
      .catch(error => console.log(error));
    event.preventDefault();
  };

  formKeyHandler = (e: SyntheticKeyboardEvent<HTMLDivElement>) => {
    //console.log(e.keyCode)
    if ((e.keyCode == 13) && (e.altKey)) {
      // eslint-disable-next-line react/no-find-dom-node
      findDOMNode(this.formb).click()
    }
  };

  render() {
    return (
      <div onKeyDown={this.formKeyHandler} style={this.props.style}>
        <Popover id="edit_pop" positionTop="-10px" positionLeft="10px" >
          <form onSubmit={this.handleSubmit} style={form_style}>
            <FormGroup ref={(node) => this.formg = node} id={"target"} />
            <Button ref={(node) => this.formb = node} type="submit" bsSize="small" bsStyle="primary"><span className="glyphicon glyphicon-save" /></Button>
          </form>
        </Popover>
      </div>
      )
  }
}