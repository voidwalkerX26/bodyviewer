// Simple test to verify frontend structure
const fs = require('fs');
const path = require('path');

function testFrontendStructure() {
  const frontendPath = './frontend';

  // Check essential files exist
  const requiredFiles = [
    'package.json',
    'tsconfig.json',
    'src/app/layout.tsx',
    'src/app/scan/page.tsx',
    'src/app/dashboard/page.tsx',
    'src/globals.css'
  ];

  let missing = [];

  for (const file of requiredFiles) {
    const fullPath = path.join(frontendPath, file);
    if (!fs.existsSync(fullPath)) {
      missing.push(file);
    }
  }

  if (missing.length > 0) {
    console.log('✗ Missing frontend files:');
    missing.forEach(file => console.log(`  - ${file}`));
    return false;
  }

  // Check package.json has required dependencies
  const pkgPath = path.join(frontendPath, 'package.json');
  const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

  const requiredDeps = ['next', 'react', 'react-dom', '@react-three/fiber', '@react-three/drei', 'three'];
  const missingDeps = requiredDeps.filter(dep => !pkg.dependencies[dep]);

  if (missingDeps.length > 0) {
    console.log('✗ Missing frontend dependencies:');
    missingDeps.forEach(dep => console.log(`  - ${dep}`));
    return false;
  }

  console.log('✓ Frontend structure looks good');
  return true;
}

if (require.main === module) {
  console.log('Testing frontend structure...\n');

  if (testFrontendStructure()) {
    console.log('\n✓ Frontend test passed!');
    console.log('\nTo start the frontend:');
    console.log('  cd frontend');
    console.log('  npm install');
    console.log('  npm run dev');
    console.log('\nThen visit: http://localhost:3000/scan');
  } else {
    process.exit(1);
  }
}

module.exports = { testFrontendStructure };