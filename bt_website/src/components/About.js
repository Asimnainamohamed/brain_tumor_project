// src/components/About.js
export default function About() {
  return (
    <div className="about">
      <h2>About This Project</h2>
      <p>
        Our AI model detects 4 types of brain conditions with 95%+ accuracy:
      </p>
      <ul>
        <li>✅ Glioma Tumor</li>
        <li>✅ Meningioma Tumor</li>
        <li>✅ Pituitary Tumor</li>
        <li>✅ No Tumor (Healthy)</li>
      </ul>
      <p>
        Built with TensorFlow, Flask, and React.
      </p>
    </div>
  );
}