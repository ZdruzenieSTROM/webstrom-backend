import React, { Component } from "react";
import ReactDOM from "react-dom";

class ExampleElement extends Component {
  render() {
    return (
      <div>
        <h4>Ukážka custom elementu vytvoreného pomocou Reactu</h4>
      </div>
    );
  }
}

// Render App component into every element with class "app"

const appElements = Array.from(document.getElementsByClassName("example-element"));

appElements.forEach((element) => {
  ReactDOM.render(<ExampleElement />, element);
});
