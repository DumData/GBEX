//@flow
"use strict";

import React from 'react'
import '../css/spinner.css'


export default function Spinner(props) {
    if (props.active) {
        return (<div id="spinner-loader"/>)
    } else {
        return null
    }
}