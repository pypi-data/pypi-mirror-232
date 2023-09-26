<template>
  <div ref="shadow"></div>
</template>
<script>
module.exports = {
  async mounted() {
    this._shadow = this.$refs.shadow.attachShadow({mode: "open"});
    this.update();
  },
  watch: {
    md(v) {
      this.update();
    }
  },
  methods: {
    async update() {
      const [marked] = await this.import(["https://cdn.jsdelivr.net/npm/marked/marked.min.js"]);
      const style = '<link rel="stylesheet" type="text/css" href="https://markdownlivepreview.com/css/github-markdown.css">';
      this._shadow.innerHTML = `${style}<div class="markdown-body">${marked.parse(this.md || "")}</div>`;
    },
    import(deps) {
      return this.loadRequire().then(
          () => {
            if (window.jupyterVue) {
              // in jupyterlab, we take Vue from ipyvue/jupyterVue
              define("vue", [], () => window.jupyterVue.Vue);
            } else {
              define("vue", ['jupyter-vue'], jupyterVue => jupyterVue.Vue);
            }
            return new Promise((resolve, reject) => {
              requirejs(deps, (...modules) => resolve(modules));
            })
          }
      );
    },
    loadRequire() {
      /* Needed in lab */
      if (window.requirejs) {
        console.log("require found");
        return Promise.resolve();
      }
      return new Promise((resolve, reject) => {
        const script = document.createElement("script");
        script.src = 'https://cdn.jsdelivr.net/npm/requirejs@2.3.6/require.min.js';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      });
    },
  }
}
</script>
