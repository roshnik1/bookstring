import "../../theme/palette-exp.css"

export default function ThemeDisplay() {
  return (
    <div>
      <div className="bg-color-key fg-color-lx">
        <h3>Key</h3>
      </div>
      <div className="bg-color-ca fg-color-lx">
        <h3>Cool A</h3>
      </div>
      <div className="bg-color-cb fg-color-lx">
        <h3>Cool B</h3>
      </div>
      <div className="bg-color-wx fg-color-lx">
        <h3>Warm X</h3>
      </div>
      <div className="bg-color-wy fg-color-lx">
        <h3>Warm Y</h3>
      </div>
      <div className="bg-color-sk fg-color-lx">
        <h3>Splash Key</h3>
      </div>
      <div className="bg-color-sa fg-color-lx">
        <h3>Splash Cool A</h3>
      </div>
      <div className="bg-color-sb fg-color-lx">
        <h3>Splash Cool B</h3>
      </div>
      <div className="bg-color-sx fg-color-lx">
        <h3>Splash Warm X</h3>
      </div>
      <div className="bg-color-sy fg-color-lx">
        <h3>Splash Warm Y</h3>
      </div>
    </div>
  )
}