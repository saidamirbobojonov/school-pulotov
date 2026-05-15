(function () {
  "use strict";

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function mulberry32(seed) {
    var a = seed >>> 0;
    return function () {
      a |= 0;
      a = (a + 0x6d2b79f5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function latLngToCanvasXY(lat, lng, width, height) {
    // Equirectangular projection
    var x = ((lng + 180) / 360) * width;
    var y = ((90 - lat) / 180) * height;
    return { x: x, y: y };
  }

  function drawLatLngPolygon(ctx, points, width, height) {
    if (!points || points.length < 3) return;
    var p0 = latLngToCanvasXY(points[0][0], points[0][1], width, height);
    ctx.beginPath();
    ctx.moveTo(p0.x, p0.y);
    for (var i = 1; i < points.length; i++) {
      var p = latLngToCanvasXY(points[i][0], points[i][1], width, height);
      ctx.lineTo(p.x, p.y);
    }
    ctx.closePath();
    ctx.fill();
  }

  function createStylizedEarthTexture(THREE) {
    var canvas = document.createElement("canvas");
    canvas.width = 1024;
    canvas.height = 512;
    var ctx = canvas.getContext("2d");
    if (!ctx) return null;

    // Water base
    var oceanGrad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    oceanGrad.addColorStop(0, "#2aa6ff");
    oceanGrad.addColorStop(1, "#0b5fa3");
    ctx.fillStyle = oceanGrad;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Subtle vignetting
    var vignette = ctx.createRadialGradient(
      canvas.width / 2,
      canvas.height / 2,
      canvas.height * 0.1,
      canvas.width / 2,
      canvas.height / 2,
      canvas.height * 0.75,
    );
    vignette.addColorStop(0, "rgba(255,255,255,0.08)");
    vignette.addColorStop(1, "rgba(0,0,0,0.25)");
    ctx.fillStyle = vignette;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Simplified continent shapes (clearer than random blobs)
    // Points are [lat, lng] and intentionally simplified for readability on a small texture.
    var continents = [
      {
        name: "NorthAmerica",
        color: "rgba(110, 200, 140, 0.95)",
        points: [
          [72, -168],
          [72, -140],
          [70, -125],
          [62, -115],
          [55, -105],
          [50, -95],
          [45, -85],
          [38, -80],
          [30, -82],
          [25, -90],
          [22, -98],
          [18, -105],
          [20, -115],
          [28, -125],
          [38, -135],
          [50, -150],
          [60, -162],
          [72, -168],
        ],
      },
      {
        name: "SouthAmerica",
        color: "rgba(90, 185, 120, 0.95)",
        points: [
          [12, -81],
          [8, -76],
          [6, -72],
          [2, -66],
          [-6, -58],
          [-14, -54],
          [-24, -52],
          [-34, -56],
          [-46, -64],
          [-55, -71],
          [-52, -75],
          [-40, -74],
          [-28, -70],
          [-18, -66],
          [-8, -70],
          [2, -76],
          [10, -80],
          [12, -81],
        ],
      },
      {
        name: "Greenland",
        color: "rgba(210, 235, 235, 0.92)",
        points: [
          [83, -74],
          [78, -28],
          [70, -18],
          [60, -35],
          [60, -60],
          [70, -74],
          [83, -74],
        ],
      },
      {
        name: "Europe",
        color: "rgba(235, 220, 130, 0.95)",
        points: [
          [71, -10],
          [71, 25],
          [66, 40],
          [60, 40],
          [56, 30],
          [52, 22],
          [48, 18],
          [45, 12],
          [43, 2],
          [36, -6],
          [43, -10],
          [55, -12],
          [63, -14],
          [71, -10],
        ],
      },
      {
        name: "Africa",
        color: "rgba(210, 190, 120, 0.95)",
        points: [
          [36, -17],
          [34, 0],
          [32, 10],
          [30, 20],
          [22, 32],
          [10, 42],
          [0, 44],
          [-10, 42],
          [-20, 35],
          [-30, 27],
          [-35, 18],
          [-35, 10],
          [-28, 2],
          [-18, -4],
          [-5, -12],
          [10, -17],
          [25, -15],
          [36, -17],
        ],
      },
      {
        name: "Asia",
        color: "rgba(150, 210, 120, 0.95)",
        points: [
          [75, 30],
          [72, 55],
          [70, 80],
          [66, 100],
          [60, 120],
          [52, 135],
          [45, 150],
          [35, 155],
          [25, 145],
          [18, 130],
          [10, 115],
          [5, 98],
          [10, 80],
          [18, 65],
          [28, 50],
          [40, 42],
          [55, 45],
          [65, 50],
          [75, 30],
        ],
      },
      {
        name: "Australia",
        color: "rgba(235, 170, 110, 0.95)",
        points: [
          [-10, 112],
          [-15, 130],
          [-20, 145],
          [-32, 154],
          [-44, 152],
          [-45, 132],
          [-42, 114],
          [-25, 112],
          [-10, 112],
        ],
      },
      {
        name: "Antarctica",
        color: "rgba(235, 245, 250, 0.92)",
        points: [
          [-60, -180],
          [-60, 180],
          [-90, 180],
          [-90, -180],
          [-60, -180],
        ],
      },
    ];

    // Land fill (each continent distinct)
    ctx.globalCompositeOperation = "source-over";
    for (var i = 0; i < continents.length; i++) {
      ctx.fillStyle = continents[i].color;
      drawLatLngPolygon(ctx, continents[i].points, canvas.width, canvas.height);
    }

    // Coastline hint (subtle)
    ctx.save();
    ctx.globalAlpha = 0.16;
    ctx.lineWidth = 2;
    ctx.strokeStyle = "rgba(255,255,255,0.65)";
    for (var j = 0; j < continents.length; j++) {
      var pts = continents[j].points;
      if (!pts || pts.length < 3) continue;
      var q0 = latLngToCanvasXY(pts[0][0], pts[0][1], canvas.width, canvas.height);
      ctx.beginPath();
      ctx.moveTo(q0.x, q0.y);
      for (var m = 1; m < pts.length; m++) {
        var q = latLngToCanvasXY(pts[m][0], pts[m][1], canvas.width, canvas.height);
        ctx.lineTo(q.x, q.y);
      }
      ctx.closePath();
      ctx.stroke();
    }
    ctx.restore();

    // Subtle land texture noise so it's not flat
    var rand = mulberry32(24681357);
    ctx.save();
    ctx.globalAlpha = 0.08;
    for (var n = 0; n < 1400; n++) {
      var x = rand() * canvas.width;
      var y = rand() * canvas.height;
      var r = 0.6 + rand() * 1.8;
      ctx.fillStyle = rand() > 0.5 ? "rgba(0,0,0,1)" : "rgba(255,255,255,1)";
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();

    var texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace || undefined;
    texture.anisotropy = 8;
    texture.needsUpdate = true;
    return texture;
  }

  function latLngToVector3(THREE, lat, lng, radius) {
    var phi = ((90 - lat) * Math.PI) / 180;
    var theta = ((lng + 180) * Math.PI) / 180;
    var x = -(radius * Math.sin(phi) * Math.cos(theta));
    var z = radius * Math.sin(phi) * Math.sin(theta);
    var y = radius * Math.cos(phi);
    return new THREE.Vector3(x, y, z);
  }

  function createGlowSprite(THREE, colorHex, opts) {
    opts = opts || {};
    var size = opts.size || 128;
    var canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    var ctx = canvas.getContext("2d");
    if (!ctx) return null;

    var grad = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
    grad.addColorStop(0, "rgba(255,255,255,0.95)");
    grad.addColorStop(0.2, "rgba(255,255,255,0.65)");
    grad.addColorStop(1, "rgba(255,255,255,0)");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, size, size);

    var texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    var material = new THREE.SpriteMaterial({
      map: texture,
      color: colorHex,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    if (opts.depthTest === false) material.depthTest = false;
    if (typeof opts.opacity === "number") material.opacity = opts.opacity;
    return new THREE.Sprite(material);
  }

  function formatLocation(city, country) {
    var parts = [];
    if (city) parts.push(city);
    if (country) parts.push(country);
    return parts.join(", ") || "";
  }

  function renderFallback(root, title, message) {
    if (!root) return;
    try {
      while (root.firstChild) root.removeChild(root.firstChild);
    } catch (e) {}

    var box = document.createElement("div");
    box.style.borderRadius = "24px";
    box.style.border = "1px solid rgba(255,255,255,0.14)";
    box.style.background = "rgba(255,255,255,0.06)";
    box.style.color = "rgba(255,255,255,0.9)";
    box.style.padding = "20px";

    var h = document.createElement("div");
    h.textContent = title || "3D globe unavailable";
    h.style.fontWeight = "700";
    h.style.marginBottom = "8px";

    var p = document.createElement("div");
    p.textContent =
      message ||
      "Required scripts failed to load. Check your network connection or allow loading React/Three.js from the CDN.";
    p.style.fontSize = "14px";
    p.style.lineHeight = "1.45";
    p.style.color = "rgba(255,255,255,0.8)";

    box.appendChild(h);
    box.appendChild(p);
    root.appendChild(box);
  }

  function createApp(root) {
    if (!root) return;
    if (!window.React || !window.ReactDOM || !window.THREE) {
      renderFallback(
        root,
        "3D globe unavailable",
        "This page couldn't load React/ReactDOM/Three.js. If your network blocks CDNs, host these libraries locally or allow unpkg.com.",
      );
      return;
    }

    var React = window.React;
    var ReactDOM = window.ReactDOM;
    var THREE = window.THREE;

    var useEffect = React.useEffect;
    var useMemo = React.useMemo;
    var useRef = React.useRef;
    var useState = React.useState;

    var apiUrl = root.getAttribute("data-api-url") || "/api/graduates/destinations/";
    var earthMapUrl = root.getAttribute("data-earth-map-url") || "";
    var earthNormalUrl = root.getAttribute("data-earth-normal-url") || "";
    var earthSpecularUrl = root.getAttribute("data-earth-specular-url") || "";

    var i18n = {};
    try {
      var scriptId = root.getAttribute("data-i18n-script-id") || "";
      if (scriptId) {
        var script = document.getElementById(scriptId);
        if (script && script.textContent) i18n = JSON.parse(script.textContent);
      } else {
        i18n = JSON.parse(root.getAttribute("data-i18n") || "{}");
      }
    } catch (e) {
      i18n = {};
    }

    function t(key, fallback) {
      var v = i18n && typeof i18n[key] === "string" ? i18n[key] : "";
      return v || fallback;
    }

    function GlobeWidget() {
      var canvasRef = useRef(null);
      var containerRef = useRef(null);
      var rafRef = useRef(0);

      var sceneRef = useRef(null);
      var cameraRef = useRef(null);
      var rendererRef = useRef(null);
      var globeRef = useRef(null);
      var atmosphereRef = useRef(null);
      var raycasterRef = useRef(new THREE.Raycaster());
      var pointerRef = useRef(new THREE.Vector2());

      var pinsGroupRef = useRef(null);
      var pinByIdRef = useRef(new Map());
      var destinationsRef = useRef([]);
      var selectedIdRef = useRef(null);
      var hoveredIdRef = useRef(null);
      var filteredByIdRef = useRef(new Map());
      var zoomRef = useRef({ min: 2.25, max: 7.2, target: 3.2 });

      var dragRef = useRef({
        active: false,
        moved: false,
        lastX: 0,
        lastY: 0,
        velocityX: 0,
        velocityY: 0,
      });

      var _a = useState([]),
        destinations = _a[0],
        setDestinations = _a[1];
      var _b = useState(null),
        selected = _b[0],
        setSelected = _b[1];
      var _c = useState(true),
        isLoading = _c[0],
        setIsLoading = _c[1];
      var _d = useState(""),
        error = _d[0],
        setError = _d[1];

      var selectedId = selected ? selected.id : null;

      useEffect(
        function () {
          destinationsRef.current = destinations || [];
        },
        [destinations],
      );

      useEffect(
        function () {
          selectedIdRef.current = selectedId;
        },
        [selectedId],
      );

      var filteredDestinations = destinations;

      useEffect(
        function () {
          var map = new Map();
          for (var i = 0; i < filteredDestinations.length; i++) {
            var d = filteredDestinations[i];
            if (d && d.id != null) map.set(String(d.id), d);
          }
          filteredByIdRef.current = map;
        },
        [filteredDestinations],
      );

      var _e = useState(null),
        hover = _e[0],
        setHover = _e[1];

      var selectedLocationTitle = useMemo(function () {
        if (!selected) return "";
        return selected.title || formatLocation(selected.city, selected.country) || "";
      }, [selected]);

      var selectedLocationSubtitle = useMemo(function () {
        if (!selected) return "";
        return formatLocation(selected.city, selected.country) || "";
      }, [selected]);

      useEffect(function () {
        var abort = new AbortController();
        setIsLoading(true);
        setError("");
        fetch(apiUrl, { signal: abort.signal, headers: { Accept: "application/json" } })
          .then(function (r) {
            if (!r.ok) throw new Error("HTTP " + r.status);
            return r.json();
          })
          .then(function (data) {
            var results = (data && data.results) || [];
            if (!Array.isArray(results)) results = [];
            setDestinations(results);
          })
          .catch(function (e) {
            if (e && e.name === "AbortError") return;
            setError(t("loadError", "Could not load destinations."));
          })
          .finally(function () {
            setIsLoading(false);
          });
        return function () {
          abort.abort();
        };
      }, [apiUrl]);

      var pupilsCount = useMemo(
        function () {
          var total = 0;
          for (var i = 0; i < filteredDestinations.length; i++) {
            var d = filteredDestinations[i];
            if (!d) continue;
            var n = 0;
            if (typeof d.graduates_count === "number") n = d.graduates_count;
            else if (d.graduates && typeof d.graduates.length === "number") n = d.graduates.length;
            total += n;
          }
          return total;
        },
        [filteredDestinations],
      );

      useEffect(function () {
        var canvas = canvasRef.current;
        var container = containerRef.current;
        if (!canvas || !container) return;

        function loadTexture(url, onLoad, onError) {
          if (!url) return;
          try {
            var loader = new THREE.TextureLoader();
            loader.load(
              url,
              function (tex) {
                if (onLoad) onLoad(tex);
              },
              undefined,
              function (err) {
                if (onError) onError(err);
              },
            );
          } catch (e) {
            if (onError) onError(e);
          }
        }

        // Scene
        var scene = new THREE.Scene();
        sceneRef.current = scene;

        var camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
        camera.position.set(0, 0, 3.2);
        cameraRef.current = camera;
        zoomRef.current.target = camera.position.z;

        var renderer = new THREE.WebGLRenderer({
          canvas: canvas,
          antialias: true,
          alpha: true,
          powerPreference: "high-performance",
        });
        rendererRef.current = renderer;
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        renderer.outputColorSpace = THREE.SRGBColorSpace || undefined;

        // Lights
        var ambient = new THREE.AmbientLight(0xffffff, 0.65);
        scene.add(ambient);
        var key = new THREE.DirectionalLight(0xffffff, 1.1);
        key.position.set(2.5, 1.4, 3.2);
        scene.add(key);
        var rim = new THREE.DirectionalLight(0x8cd6ff, 0.55);
        rim.position.set(-3.2, 0.2, -2.4);
        scene.add(rim);

        // Globe
        var globeGroup = new THREE.Group();
        globeRef.current = globeGroup;
        scene.add(globeGroup);

        var earthTexture = createStylizedEarthTexture(THREE);
        var earthGeo = new THREE.SphereGeometry(1, 64, 64);
        var earthMat = new THREE.MeshStandardMaterial({
          map: earthTexture || null,
          color: earthTexture ? 0xffffff : 0x2aa6ff,
          roughness: 0.78,
          metalness: 0.05,
        });
        var earth = new THREE.Mesh(earthGeo, earthMat);
        earth.castShadow = false;
        earth.receiveShadow = false;
        globeGroup.add(earth);

        // Load realistic Earth textures (equirectangular) if provided.
        loadTexture(
          earthMapUrl,
          function (tex) {
            tex.colorSpace = THREE.SRGBColorSpace || undefined;
            tex.anisotropy = 8;
            tex.needsUpdate = true;
            earthMat.map = tex;
            earthMat.color.set(0xffffff);
            earthMat.needsUpdate = true;
          },
          function () {},
        );
        loadTexture(
          earthNormalUrl,
          function (tex) {
            tex.anisotropy = 8;
            tex.needsUpdate = true;
            earthMat.normalMap = tex;
            if (earthMat.normalScale && earthMat.normalScale.set) earthMat.normalScale.set(0.6, 0.6);
            earthMat.needsUpdate = true;
          },
          function () {},
        );
        loadTexture(
          earthSpecularUrl,
          function (tex) {
            // Convert "specular" map into roughness influence by reusing it as roughnessMap.
            // Brighter specular => smoother surface (lower roughness). This isn't perfect but adds realism.
            tex.anisotropy = 8;
            tex.needsUpdate = true;
            earthMat.roughnessMap = tex;
            earthMat.roughness = 0.85;
            earthMat.metalness = 0.02;
            earthMat.needsUpdate = true;
          },
          function () {},
        );

        // Atmosphere
        var atmoGeo = new THREE.SphereGeometry(1.04, 64, 64);
        var atmoMat = new THREE.MeshBasicMaterial({
          color: 0x86dcff,
          transparent: true,
          opacity: 0.12,
          blending: THREE.AdditiveBlending,
          side: THREE.BackSide,
          depthWrite: false,
        });
        var atmo = new THREE.Mesh(atmoGeo, atmoMat);
        atmosphereRef.current = atmo;
        globeGroup.add(atmo);

        // Pins group
        var pinsGroup = new THREE.Group();
        pinsGroupRef.current = pinsGroup;
        globeGroup.add(pinsGroup);

        var tmpScale = new THREE.Vector3(1, 1, 1);

        // Resize
        function resize() {
          var rect = container.getBoundingClientRect();
          var width = Math.max(1, Math.floor(rect.width));
          var height = Math.max(1, Math.floor(rect.height));
          camera.aspect = width / height;
          camera.updateProjectionMatrix();
          renderer.setSize(width, height, false);
        }

        var ro = new ResizeObserver(resize);
        ro.observe(container);
        resize();

        // Render loop
        function animate() {
          rafRef.current = window.requestAnimationFrame(animate);

          // Idle rotation / inertia
          var drag = dragRef.current;
          if (!drag.active) {
            drag.velocityX *= 0.92;
            drag.velocityY *= 0.92;
            globeGroup.rotation.y += drag.velocityX;
            globeGroup.rotation.x += drag.velocityY;
            globeGroup.rotation.x = clamp(globeGroup.rotation.x, -0.85, 0.85);
            if (Math.abs(drag.velocityX) < 0.00002) globeGroup.rotation.y += 0.0012;
          }

          // Highlight selected
          var sid = selectedIdRef.current;
          var now = Date.now();
          var tt = now * 0.0032;
          pinByIdRef.current.forEach(function (node, id) {
            var isSelected = sid != null && String(id) === String(sid);
            var phase = (node.userData && node.userData.phase) || 0;
            var wobble = (Math.sin(tt + phase) + 1) * 0.5; // 0..1
            var baseScale = (node.userData && node.userData.baseScale) || 1;
            var target = baseScale * (isSelected ? 1.55 : 1.0);
            tmpScale.set(target, target, target);
            node.scale.lerp(tmpScale, 0.1);

            if (node.userData) {
              var halo = node.userData.halo;
              if (halo) {
                halo.scale.setScalar(isSelected ? 0.34 + Math.sin(now / 220) * 0.06 : 0.26 + wobble * 0.05);
                if (halo.material) halo.material.opacity = isSelected ? 0.6 : 0.22;
              }
            }
          });

          // Camera zoom easing
          var z = zoomRef.current;
          var dz = z.target - camera.position.z;
          if (Math.abs(dz) > 0.0002) camera.position.z += dz * 0.14;

          renderer.render(scene, camera);
        }

        animate();

        // Input helpers
        function setPointerFromEvent(event) {
          var rect = canvas.getBoundingClientRect();
          var x = (event.clientX - rect.left) / rect.width;
          var y = (event.clientY - rect.top) / rect.height;
          pointerRef.current.set(x * 2 - 1, -(y * 2 - 1));
        }

        function pick(event) {
          setPointerFromEvent(event);
          var raycaster = raycasterRef.current;
          raycaster.setFromCamera(pointerRef.current, camera);
          var hits = raycaster.intersectObjects(pinsGroup.children, true);
          if (!hits || !hits.length) return null;
          var o = hits[0].object;
          while (o && o.parent && !o.userData.destinationId) o = o.parent;
          return o && o.userData ? o.userData.destinationId : null;
        }

        function onPointerDown(e) {
          var drag = dragRef.current;
          drag.active = true;
          drag.moved = false;
          drag.lastX = e.clientX;
          drag.lastY = e.clientY;
          drag.velocityX = 0;
          drag.velocityY = 0;
          hoveredIdRef.current = null;
          setHover(null);
          canvas.setPointerCapture && canvas.setPointerCapture(e.pointerId);
        }

        function onPointerMove(e) {
          var drag = dragRef.current;
          if (drag.active) {
            var dx = e.clientX - drag.lastX;
            var dy = e.clientY - drag.lastY;
            drag.lastX = e.clientX;
            drag.lastY = e.clientY;
            if (Math.abs(dx) + Math.abs(dy) > 6) drag.moved = true;

            var rotY = dx * 0.006;
            var rotX = dy * 0.005;
            globeGroup.rotation.y += rotY;
            globeGroup.rotation.x += rotX;
            globeGroup.rotation.x = clamp(globeGroup.rotation.x, -0.85, 0.85);

            drag.velocityX = rotY;
            drag.velocityY = rotX;
            return;
          }

          var id = pick(e);
          var key = id == null ? null : String(id);
          if (hoveredIdRef.current === key) return;
          hoveredIdRef.current = key;

          if (id == null) {
            setHover(null);
            return;
          }

          var d = filteredByIdRef.current.get(String(id));
          if (!d) {
            setHover(null);
            return;
          }

          var rect = canvas.getBoundingClientRect();
          setHover({
            text: formatLocation(d.city, d.country),
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
          });
        }

        function onPointerUp(e) {
          var drag = dragRef.current;
          drag.active = false;
          if (!drag.moved) {
            var id = pick(e);
            if (id != null) {
              var list = destinationsRef.current || [];
              var pid = id;
              if (typeof pid === "string") {
                var n = parseInt(pid, 10);
                if (!isNaN(n)) pid = n;
              }
              var found = list.find(function (d) {
                return d && (d.id === pid || String(d.id) === String(id));
              });
              if (found) {
                var current = selectedIdRef.current;
                if (current != null && String(current) === String(found.id)) setSelected(null);
                else setSelected(found);
              }
            }
          }
        }

        function onPointerLeave() {
          hoveredIdRef.current = null;
          setHover(null);
        }

        function onWheel(e) {
          try {
            e.preventDefault();
          } catch (err) {}
          var z = zoomRef.current;
          // deltaY > 0 => zoom out (increase distance)
          var next = z.target + (e.deltaY || 0) * 0.0025;
          z.target = clamp(next, z.min, z.max);
        }

        canvas.addEventListener("pointerdown", onPointerDown);
        canvas.addEventListener("pointermove", onPointerMove);
        canvas.addEventListener("pointerup", onPointerUp);
        canvas.addEventListener("pointercancel", onPointerUp);
        canvas.addEventListener("pointerleave", onPointerLeave);
        canvas.addEventListener("wheel", onWheel, { passive: false });

        return function cleanup() {
          window.cancelAnimationFrame(rafRef.current);
          canvas.removeEventListener("pointerdown", onPointerDown);
          canvas.removeEventListener("pointermove", onPointerMove);
          canvas.removeEventListener("pointerup", onPointerUp);
          canvas.removeEventListener("pointercancel", onPointerUp);
          canvas.removeEventListener("pointerleave", onPointerLeave);
          canvas.removeEventListener("wheel", onWheel);
          ro.disconnect();

          // Dispose
          pinByIdRef.current.clear();
          try {
            renderer.dispose();
          } catch (e) {}
          scene.traverse(function (obj) {
            if (obj.geometry) {
              try {
                obj.geometry.dispose();
              } catch (e) {}
            }
            if (obj.material) {
              var mats = Array.isArray(obj.material) ? obj.material : [obj.material];
              mats.forEach(function (m) {
                if (!m) return;
                ["map", "normalMap", "roughnessMap", "metalnessMap", "emissiveMap", "alphaMap", "aoMap", "bumpMap"].forEach(
                  function (k) {
                    if (m[k] && m[k].dispose) {
                      try {
                        m[k].dispose();
                      } catch (e) {}
                    }
                  },
                );
                try {
                  m.dispose();
                } catch (e) {}
              });
            }
          });
        };
      }, []);

      // Update pins when destinations change (or when scene becomes ready)
      useEffect(function () {
        var pinsGroup = pinsGroupRef.current;
        if (!pinsGroup) return;

        // Clear existing
        while (pinsGroup.children.length) pinsGroup.remove(pinsGroup.children[0]);
        pinByIdRef.current.clear();

        var headGeo = new THREE.SphereGeometry(0.052, 22, 22);
        var stemGeo = new THREE.CylinderGeometry(0.012, 0.012, 0.22, 16, 1, false);
        var pinMat = new THREE.MeshStandardMaterial({
          color: 0xf6b547,
          emissive: 0xf6b547,
          emissiveIntensity: 0.9,
          roughness: 0.35,
          metalness: 0.12,
        });

        for (var i = 0; i < filteredDestinations.length; i++) {
          var d = filteredDestinations[i];
          if (!d || typeof d.latitude !== "number" || typeof d.longitude !== "number") continue;
          var lat = clamp(d.latitude, -90, 90);
          var lng = clamp(d.longitude, -180, 180);

          var group = new THREE.Group();
          group.userData = { destinationId: d.id, halo: null, phase: (Number(d.id) || i) * 0.9, baseScale: 1 };

          // Stem (points outward along +Z after lookAt)
          var stem = new THREE.Mesh(stemGeo, pinMat);
          stem.rotation.x = Math.PI / 2;
          stem.position.z = 0.11;
          group.add(stem);

          // Head
          var head = new THREE.Mesh(headGeo, pinMat);
          head.position.z = 0.24;
          group.add(head);

          // Halo (billboard sprite)
          var halo = createGlowSprite(THREE, 0xf6b547, { size: 192, opacity: 0.22, depthTest: false });
          if (halo) {
            halo.scale.setScalar(0.26);
            halo.position.z = 0.24;
            group.add(halo);
            group.userData.halo = halo;
          }

          var pos = latLngToVector3(THREE, lat, lng, 1.02);
          group.position.copy(pos);
          group.lookAt(0, 0, 0);

          pinsGroup.add(group);
          pinByIdRef.current.set(d.id, group);
        }
      }, [filteredDestinations]);

      var featuredImage = selected && selected.image_url ? selected.image_url : "";
      var featuredDescription = selected && selected.description ? selected.description : "";
      var selectedGraduates = (selected && selected.graduates) || [];

      var visibleGraduates = useMemo(
        function () {
          return (selectedGraduates || []).filter(function (g) {
            return g && g.full_name;
          });
        },
        [selectedGraduates],
      );
      var graduatesPanel = useMemo(
        function () {
          if (!visibleGraduates || !visibleGraduates.length) return null;
          var group = selected && selected.id != null ? "dest-" + String(selected.id) : "dest";
          var cards = visibleGraduates.map(function (g, idx) {
            var photos = [];
            if (g.photo_1_url) photos.push(g.photo_1_url);
            if (g.photo_2_url) photos.push(g.photo_2_url);

            var meta = [];
            if (g.graduation_year) meta.push(t("gradYear", "Class of ") + g.graduation_year);
            if (g.university_name) meta.push(g.university_name);

            var extra = [];
            if (g.degree) extra.push(g.degree);
            if (g.program) extra.push(g.program);
            if (g.start_year) extra.push(String(g.start_year));

            return React.createElement(
              "div",
              {
                key:
                  g && g.id != null
                    ? g.id
                    : (g.full_name || "graduate") + "-" + String(g.graduation_year || "") + "-" + String(idx),
                className:
                  "rounded-2xl border border-gray-100 dark:border-[#332e2b] bg-gray-50/60 dark:bg-white/5 overflow-hidden",
              },
              photos.length
                ? React.createElement(
                    "div",
                    { className: "grid grid-cols-2 gap-1" },
                    photos.slice(0, 2).map(function (src, pidx) {
                      return React.createElement(
                        "button",
                        {
                          key: String(pidx) + "-" + src,
                          type: "button",
                          className:
                            "block w-full focus:outline-none focus:ring-2 focus:ring-primary/70",
                          "data-lightbox-item": "true",
                          "data-lightbox-group": group,
                          "data-lightbox-src": src,
                          "data-lightbox-alt": g.full_name || "",
                          "data-lightbox-caption": (g.full_name || "").trim(),
                          "aria-label": g.full_name || "",
                        },
                        React.createElement("img", {
                          src: src,
                          alt: g.full_name || "",
                          className: "w-full h-28 object-cover",
                          loading: "lazy",
                        }),
                      );
                    }),
                  )
                : null,
              React.createElement(
                "div",
                { className: "p-4" },
                React.createElement("div", { className: "font-bold text-[#0b1020] dark:text-white" }, g.full_name),
                meta.length
                  ? React.createElement(
                      "div",
                      { className: "text-sm text-gray-600 dark:text-gray-300 mt-1" },
                      meta.join(" · "),
                    )
                  : null,
                extra.length
                  ? React.createElement(
                      "div",
                      { className: "text-xs text-gray-500 dark:text-gray-400 mt-2" },
                      extra.join(" · "),
                    )
                  : null,
              ),
            );
          });

          return React.createElement(
            "div",
            { className: "mt-8" },
            React.createElement(
              "div",
              { className: "text-xs font-bold tracking-widest uppercase text-gray-500 dark:text-gray-400 mb-3" },
              t("pupilsTitle", "Pupils"),
            ),
            React.createElement("div", { className: "space-y-3" }, cards),
          );
        },
        [visibleGraduates, selected],
      );

      function zoomBy(delta) {
        var z = zoomRef.current;
        z.target = clamp(z.target + delta, z.min, z.max);
      }

      return React.createElement(
        "div",
        { className: "w-full" },
        React.createElement(
          "div",
          { className: selected ? "grid grid-cols-1 lg:grid-cols-[1.2fr_0.8fr] gap-6 items-stretch" : "grid grid-cols-1" },
          React.createElement(
            "div",
            {
              className:
                "relative rounded-3xl overflow-hidden bg-gradient-to-br from-[#0b1020] via-[#0b1020] to-[#131b32] border border-white/10 shadow-2xl min-h-[520px] lg:min-h-[700px]",
              style: {
                position: "relative",
                minHeight: "520px",
                height: "clamp(520px, 70vh, 760px)",
              },
            },
            React.createElement(
              "div",
              { ref: containerRef, className: "absolute inset-0", style: { position: "absolute", inset: 0 } },
              React.createElement("canvas", {
                ref: canvasRef,
                className: "w-full h-full block",
                style: { display: "block", width: "100%", height: "100%" },
                role: "img",
                "aria-label": t("globeAria", "3D globe showing graduate destinations"),
              }),
            ),
            hover && hover.text
              ? React.createElement(
                  "div",
                  {
                    className:
                      "pointer-events-none absolute z-20 px-3 py-2 rounded-xl bg-black/70 text-white text-xs font-semibold backdrop-blur-sm border border-white/10",
                    style: {
                      left: Math.max(12, Math.min((hover.x || 0) + 14, 760)),
                      top: Math.max(12, (hover.y || 0) - 10),
                      transform: "translateY(-100%)",
                      maxWidth: "260px",
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    },
                  },
                  hover.text,
                )
              : null,
            React.createElement(
              "div",
              {
                className: "absolute bottom-6 left-6 right-6 flex items-center justify-end gap-3",
                style: { position: "absolute", left: 24, right: 24, bottom: 24 },
              },
              React.createElement(
                "div",
                { className: "flex items-center gap-2" },
                React.createElement(
                  "button",
                  {
                    type: "button",
                    "aria-label": t("zoomIn", "Zoom in"),
                    onClick: function () {
                      zoomBy(-0.35);
                    },
                    className:
                      "inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 border border-white/15 text-white transition-colors",
                  },
                  React.createElement("span", { className: "material-symbols-outlined text-[22px]" }, "zoom_in"),
                ),
                React.createElement(
                  "button",
                  {
                    type: "button",
                    "aria-label": t("zoomOut", "Zoom out"),
                    onClick: function () {
                      zoomBy(0.35);
                    },
                    className:
                      "inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 border border-white/15 text-white transition-colors",
                  },
                  React.createElement("span", { className: "material-symbols-outlined text-[22px]" }, "zoom_out"),
                ),
              ),
              React.createElement(
                "div",
                { className: "flex items-center gap-2 text-white/70 text-xs" },
                React.createElement(
                  "span",
                  {
                    className:
                      "inline-flex items-center justify-center w-7 h-7 rounded-full bg-white/10 border border-white/15",
                  },
                  React.createElement("span", { className: "material-symbols-outlined text-[18px]" }, "public"),
                ),
                React.createElement(
                  "span",
                  null,
                  t("pupilsCount", "Pupils: ") + String(pupilsCount || 0),
                ),
              ),
            ),
          ),
          selected
            ? React.createElement(
                "div",
                {
                  className:
                    "rounded-3xl overflow-hidden bg-white dark:bg-[#1a1614] border border-gray-100 dark:border-[#332e2b] shadow-2xl",
                },
                React.createElement(
                  "div",
                  { className: "p-6 md:p-8" },
                  React.createElement(
                    React.Fragment,
                    null,
                    React.createElement(
                      "div",
                      { className: "flex items-start justify-between gap-3" },
                      React.createElement(
                        "div",
                        { className: "text-xs font-bold tracking-widest uppercase text-gray-500 dark:text-gray-400 mt-2" },
                        t("infoTitle", "Information"),
                      ),
                      React.createElement(
                        "button",
                        {
                          type: "button",
                          "aria-label": t("close", "Close"),
                          onClick: function () {
                            setSelected(null);
                          },
                          className:
                            "inline-flex items-center justify-center w-10 h-10 rounded-full border border-gray-200 dark:border-[#332e2b] text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5",
                        },
                        React.createElement("span", { className: "material-symbols-outlined text-[20px]" }, "close"),
                      ),
                    ),
                    featuredImage
                      ? React.createElement(
                          "div",
                          { className: "rounded-2xl overflow-hidden border border-gray-100 dark:border-[#332e2b] mt-4" },
                          React.createElement("img", {
                            src: featuredImage,
                            alt: selectedLocationTitle || "",
                            className: "w-full h-56 object-cover",
                            loading: "lazy",
                          }),
                        )
                      : null,
                    selectedLocationSubtitle
                      ? React.createElement(
                          "div",
                          { className: featuredImage ? "mt-6" : "" },
                          React.createElement(
                            "div",
                            { className: "text-sm font-semibold text-gray-600 dark:text-gray-300" },
                            selectedLocationSubtitle,
                          ),
                          selectedLocationTitle && selectedLocationTitle !== selectedLocationSubtitle
                            ? React.createElement(
                                "h3",
                                {
                                  className:
                                    "text-2xl md:text-3xl font-bold text-[#0b1020] dark:text-white mt-1 leading-tight",
                                },
                                selectedLocationTitle,
                              )
                            : null,
                          featuredDescription
                            ? React.createElement(
                                "p",
                                {
                                  className:
                                    "mt-4 text-sm md:text-base text-gray-600 dark:text-gray-400 leading-relaxed",
                                },
                                featuredDescription,
                              )
                            : null,
                        )
                      : selectedLocationTitle || featuredDescription
                        ? React.createElement(
                            "div",
                            { className: featuredImage ? "mt-6" : "" },
                            selectedLocationTitle
                              ? React.createElement(
                                  "h3",
                                  {
                                    className:
                                      "text-2xl md:text-3xl font-bold text-[#0b1020] dark:text-white leading-tight",
                                  },
                                  selectedLocationTitle,
                                )
                              : null,
                              featuredDescription
                                ? React.createElement(
                                    "p",
                                    {
                                      className:
                                        "mt-4 text-sm md:text-base text-gray-600 dark:text-gray-400 leading-relaxed",
                                    },
                                    featuredDescription,
                                  )
                                : null,
                          )
                        : null,
                    graduatesPanel,
                  ),
                ),
              )
            : null,
        ),
      );
    }

    var rootEl = ReactDOM.createRoot ? ReactDOM.createRoot(root) : null;
    if (rootEl) {
      rootEl.render(React.createElement(GlobeWidget, null));
    } else if (ReactDOM.render) {
      ReactDOM.render(React.createElement(GlobeWidget, null), root);
    }
  }

  function boot() {
    var root = document.getElementById("graduates-globe-root");
    if (!root) return;
    createApp(root);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
