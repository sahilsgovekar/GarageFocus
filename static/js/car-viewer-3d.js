/**
 * 3D Car Viewer for Garage Focus
 * Uses Three.js for interactive 3D car viewing
 */

class Car3DViewer {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            width: options.width || this.container.clientWidth,
            height: options.height || this.container.clientHeight || 400,
            enableControls: options.enableControls !== false,
            autoRotate: options.autoRotate || false,
            showProgress: options.showProgress !== false,
            fallbackMode: options.fallbackMode || 'image'
        };
        
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.currentModel = null;
        this.animationId = null;
        this.isLoading = false;
        
        this.init();
    }
    
    init() {
        // Check if Three.js is available
        if (typeof THREE === 'undefined') {
            console.warn('Three.js not loaded, falling back to 2D mode');
            this.enableFallback();
            return;
        }
        
        this.setupScene();
        this.setupCamera();
        this.setupRenderer();
        this.setupControls();
        this.setupLights();
        this.setupEventListeners();
        
        // Start render loop
        this.animate();
    }
    
    setupScene() {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a1a); // garage-dark color
        
        // Add subtle fog for depth
        this.scene.fog = new THREE.Fog(0x1a1a1a, 1, 100);
    }
    
    setupCamera() {
        const aspect = this.options.width / this.options.height;
        this.camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 1000);
        this.camera.position.set(5, 2, 5);
        this.camera.lookAt(0, 0, 0);
    }
    
    setupRenderer() {
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true, 
            alpha: true 
        });
        this.renderer.setSize(this.options.width, this.options.height);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.outputEncoding = THREE.sRGBEncoding;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
        
        this.container.appendChild(this.renderer.domElement);
    }
    
    setupControls() {
        if (!this.options.enableControls || typeof THREE.OrbitControls === 'undefined') {
            return;
        }
        
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.enableZoom = true;
        this.controls.enablePan = false;
        this.controls.autoRotate = this.options.autoRotate;
        this.controls.autoRotateSpeed = 1.0;
        this.controls.minDistance = 3;
        this.controls.maxDistance = 15;
        this.controls.minPolarAngle = Math.PI / 6;  // 30 degrees
        this.controls.maxPolarAngle = Math.PI / 2;  // 90 degrees
    }
    
    setupLights() {
        // Ambient light for overall illumination
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // Main directional light (key light)
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.0);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.camera.near = 0.1;
        directionalLight.shadow.camera.far = 50;
        directionalLight.shadow.camera.left = -10;
        directionalLight.shadow.camera.right = 10;
        directionalLight.shadow.camera.top = 10;
        directionalLight.shadow.camera.bottom = -10;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        this.scene.add(directionalLight);
        
        // Fill light
        const fillLight = new THREE.DirectionalLight(0x00d9ff, 0.3); // neon-cyan
        fillLight.position.set(-5, 5, -5);
        this.scene.add(fillLight);
        
        // Rim light for definition
        const rimLight = new THREE.DirectionalLight(0xffb000, 0.2); // neon-amber
        rimLight.position.set(0, 5, -10);
        this.scene.add(rimLight);
    }
    
    setupEventListeners() {
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Handle container resize
        if (window.ResizeObserver) {
            const resizeObserver = new ResizeObserver(() => this.onWindowResize());
            resizeObserver.observe(this.container);
        }
    }
    
    onWindowResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight || this.options.height;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        if (this.controls) {
            this.controls.update();
        }
        
        // Add subtle rotation to the car if no user interaction
        if (this.currentModel && this.options.autoRotate && !this.controls?.autoRotate) {
            this.currentModel.rotation.y += 0.005;
        }
        
        this.renderer.render(this.scene, this.camera);
    }
    
    async loadCarModel(modelUrl, progress = 0) {
        if (this.isLoading) return;
        
        this.showLoadingState();
        this.isLoading = true;
        
        try {
            // Remove existing model
            if (this.currentModel) {
                this.scene.remove(this.currentModel);
                this.disposeMaterial(this.currentModel);
            }
            
            // Determine file type and load accordingly
            const fileExt = modelUrl.split('.').pop().toLowerCase();
            
            if (fileExt === 'glb' || fileExt === 'gltf') {
                await this.loadGLTFModel(modelUrl, progress);
            } else if (fileExt === 'fbx') {
                await this.loadFBXModel(modelUrl, progress);
            } else if (fileExt === 'obj') {
                await this.loadOBJModel(modelUrl, progress);
            } else {
                throw new Error(`Unsupported model format: ${fileExt}`);
            }
            
            this.hideLoadingState();
            
        } catch (error) {
            console.error('Error loading 3D model:', error);
            this.showError('Failed to load 3D model');
            this.hideLoadingState();
        }
        
        this.isLoading = false;
    }
    
    async loadGLTFModel(url, progress) {
        return new Promise((resolve, reject) => {
            const loader = new THREE.GLTFLoader();
            
            loader.load(
                url,
                (gltf) => {
                    this.currentModel = gltf.scene;
                    this.processLoadedModel(progress);
                    resolve(gltf);
                },
                (progress) => {
                    // Loading progress callback
                    const percent = (progress.loaded / progress.total) * 100;
                    this.updateLoadingProgress(percent);
                },
                (error) => {
                    reject(error);
                }
            );
        });
    }
    
    async loadFBXModel(url, progress) {
        return new Promise((resolve, reject) => {
            if (typeof THREE.FBXLoader === 'undefined') {
                reject(new Error('FBXLoader not available'));
                return;
            }
            
            const loader = new THREE.FBXLoader();
            loader.load(url, (fbx) => {
                this.currentModel = fbx;
                this.processLoadedModel(progress);
                resolve(fbx);
            }, undefined, reject);
        });
    }
    
    async loadOBJModel(url, progress) {
        return new Promise((resolve, reject) => {
            if (typeof THREE.OBJLoader === 'undefined') {
                reject(new Error('OBJLoader not available'));
                return;
            }
            
            const loader = new THREE.OBJLoader();
            loader.load(url, (obj) => {
                this.currentModel = obj;
                this.processLoadedModel(progress);
                resolve(obj);
            }, undefined, reject);
        });
    }
    
    processLoadedModel(progress) {
        if (!this.currentModel) return;
        
        // Center and scale the model
        const box = new THREE.Box3().setFromObject(this.currentModel);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        // Center the model
        this.currentModel.position.sub(center);
        
        // Scale to fit in view
        const maxDim = Math.max(size.x, size.y, size.z);
        const targetSize = 3;
        if (maxDim > 0) {
            this.currentModel.scale.setScalar(targetSize / maxDim);
        }
        
        // Apply progression-based material modifications
        this.applyProgressionEffects(progress);
        
        // Enable shadows
        this.currentModel.traverse((child) => {
            if (child.isMesh) {
                child.castShadow = true;
                child.receiveShadow = true;
            }
        });
        
        this.scene.add(this.currentModel);
    }
    
    applyProgressionEffects(progress) {
        if (!this.currentModel) return;
        
        this.currentModel.traverse((child) => {
            if (child.isMesh && child.material) {
                const material = child.material.clone();
                
                // Apply rust/restoration effects based on progress
                if (progress < 25) {
                    // Rusted state
                    material.color.setHex(0x8B4513); // Dark brown/rust
                    material.roughness = 0.9;
                    material.metalness = 0.1;
                } else if (progress < 50) {
                    // Primer state
                    material.color.setHex(0x696969); // Gray primer
                    material.roughness = 0.7;
                    material.metalness = 0.3;
                } else if (progress < 75) {
                    // Base paint
                    material.color.setHex(0x1E90FF); // Dodger blue
                    material.roughness = 0.4;
                    material.metalness = 0.6;
                } else if (progress < 100) {
                    // Nearly complete
                    material.color.setHex(0x0066CC); // Rich blue
                    material.roughness = 0.2;
                    material.metalness = 0.8;
                } else {
                    // Showroom ready
                    material.color.setHex(0x003399); // Deep blue
                    material.roughness = 0.1;
                    material.metalness = 0.9;
                    
                    // Add some sparkle for completed cars
                    if (material.map) {
                        material.envMapIntensity = 1.0;
                    }
                }
                
                child.material = material;
            }
        });
    }
    
    showLoadingState() {
        const loadingEl = this.container.querySelector('.loading-3d') || this.createLoadingElement();
        loadingEl.classList.remove('hidden');
        
        // Auto-timeout after 3 seconds if no progress
        setTimeout(() => {
            if (!this.currentModel) {
                console.warn('3D loading timeout, switching to fallback');
                this.hideLoadingState();
                this.enableFallback();
            }
        }, 3000);
    }
    
    hideLoadingState() {
        const loadingEl = this.container.querySelector('.loading-3d');
        if (loadingEl) {
            loadingEl.classList.add('hidden');
        }
    }
    
    createLoadingElement() {
        const loadingEl = document.createElement('div');
        loadingEl.className = 'loading-3d absolute inset-0 flex items-center justify-center bg-garage-darker bg-opacity-75 z-10';
        loadingEl.innerHTML = `
            <div class="text-center">
                <div class="text-4xl mb-2">⚙️</div>
                <div class="text-neon-cyan font-semibold">Loading 3D Model...</div>
                <div class="loading-progress mt-2 text-sm text-gray-400">0%</div>
            </div>
        `;
        this.container.appendChild(loadingEl);
        return loadingEl;
    }
    
    updateLoadingProgress(percent) {
        const progressEl = this.container.querySelector('.loading-progress');
        if (progressEl) {
            progressEl.textContent = `${Math.round(percent)}%`;
        }
    }
    
    showError(message) {
        const errorEl = document.createElement('div');
        errorEl.className = 'error-3d absolute inset-0 flex items-center justify-center bg-rust-red bg-opacity-20 z-10';
        errorEl.innerHTML = `
            <div class="text-center text-rust-red">
                <div class="text-4xl mb-2">⚠️</div>
                <div class="font-semibold">${message}</div>
                <button onclick="this.parentElement.parentElement.remove()" class="mt-2 text-sm underline">Close</button>
            </div>
        `;
        this.container.appendChild(errorEl);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorEl.parentElement) {
                errorEl.remove();
            }
        }, 5000);
    }
    
    enableFallback() {
        // Create fallback 2D display
        this.container.innerHTML = `
            <div class="fallback-viewer w-full h-full flex items-center justify-center bg-garage-dark rounded-lg border border-gray-600">
                <div class="text-center">
                    <div class="text-6xl mb-4 car-emoji">🚗</div>
                    <p class="text-gray-400">3D viewer not available</p>
                    <p class="text-sm text-gray-500">Using 2D fallback mode</p>
                </div>
            </div>
        `;
    }
    
    updateProgress(progress) {
        if (this.currentModel) {
            this.applyProgressionEffects(progress);
        }
        
        // Update fallback emoji if in 2D mode
        const carEmoji = this.container.querySelector('.car-emoji');
        if (carEmoji) {
            if (progress < 25) {
                carEmoji.textContent = '🚗💨'; // Smoking
            } else if (progress < 50) {
                carEmoji.textContent = '🔧🚗'; // Being worked on
            } else if (progress < 75) {
                carEmoji.textContent = '🚙'; // SUV/better car
            } else if (progress < 100) {
                carEmoji.textContent = '🚗✨'; // Almost done
            } else {
                carEmoji.textContent = '🏁🚗🏁'; // Showroom ready
            }
        }
    }
    
    disposeMaterial(object) {
        object.traverse((child) => {
            if (child.isMesh) {
                if (child.geometry) {
                    child.geometry.dispose();
                }
                if (child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach(material => material.dispose());
                    } else {
                        child.material.dispose();
                    }
                }
            }
        });
    }
    
    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        
        if (this.currentModel) {
            this.disposeMaterial(this.currentModel);
            this.scene.remove(this.currentModel);
        }
        
        if (this.renderer) {
            this.renderer.dispose();
        }
        
        if (this.controls) {
            this.controls.dispose();
        }
        
        // Clear container
        this.container.innerHTML = '';
    }
}

// Make it globally available
window.Car3DViewer = Car3DViewer;
