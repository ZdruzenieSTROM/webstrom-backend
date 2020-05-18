import React, { Component } from "react";
import ReactDOM from "react-dom";

export class Mathjax extends Component {
  constructor(props) {
    super(props);
    this.node = React.createRef();
  }

  componentDidMount() {
    this.renderMath();
  }

  componentDidUpdate() {
    this.renderMath();
  }

  renderMath() {
    if (window.MathJax !== undefined) {
      window.MathJax.Hub.Queue(["Typeset", window.MathJax.Hub, this.node.current]);
    }
  }

  render() {
    return <div ref={this.node}>{this.props.children}</div>;
  }
}

export default class LatexElement extends Component {
  render() {
    return <Mathjax>{this.props.children}</Mathjax>;
  }
}

// Render App component into every element with class "app"

const latex_elements = Array.from(document.getElementsByClassName("latex-element"));

latex_elements.forEach((element) => {
  element.classList.add("mathjax");
  ReactDOM.render(<LatexElement>{element.innerHTML}</LatexElement>, element);
});
