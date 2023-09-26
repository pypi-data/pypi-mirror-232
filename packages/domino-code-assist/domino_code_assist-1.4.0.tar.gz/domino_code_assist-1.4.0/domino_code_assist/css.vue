<template>
</template>
<style id="domino-css">
  .domino-plotly-auto-height .js-plotly-plot {
    height: 100%;
  }

  .domino-card-grid .modebar-container {
    display: none;
  }
  .dca-transform-header {
    background-color: var(--jp-border-color3);
  }
  .milkdown-menu .button.active {
    background-color: var(--jp-border-color2);
  }

  .domino-thumbnail .js-plotly-plot {
    height: 100%;
  }
  .domino-thumbnail .js-plotly-plot .plot-container.plotly {
    height: 100%;
  }
  .domino-ml-model-type-button {
    cursor: pointer;
  }
  .domino-ml-model-type-button:hover {
    background-color: var(--jp-border-color2);
  }
  .dca-ml-task-selection .v-stepper__content,
  .vuetify-styles .v-dialog>.dca-ml-task-selection.v-card .v-card__text {
    padding: 0
  }
  .dca-automl-config .v-expansion-panel-header .v-chip {
    overflow: unset;
  }
  .vuetify-styles .dca-hyperparameters-checkbox.v-input--selection-controls {
    margin: 0;
  }
  .dca-hyperparameters-list {
    transition: opacity 0.5s;
  }
  .dca-hyperparameters-list-off {
    opacity: 0.5;
    pointer-events:none;
  }

  .vuetify-styles .v-dialog>.v-card.dca-foundation-drawer>.v-card__text {
    padding-right: 0;
    padding-left: 0;
  }

  .dca-foundation-drawer-content.v-stepper,
  .dca-foundation-drawer-content .v-stepper__items,
  .dca-foundation-drawer-content .v-stepper__content,
  .dca-foundation-drawer-content .v-stepper__wrapper {
    height: 100%;
  }

  table.dcs-foundation-data-preview {
    width: 100%;
  }
  table.dcs-foundation-data-preview td,
  table.dcs-foundation-data-preview th {
    padding: 4px;
    white-space: nowrap;
    max-width: 0;
    text-overflow: ellipsis;
    overflow: hidden;
  }
  table.dcs-foundation-data-preview tbody tr:nth-child(even) {
    background: var(--jp-border-color3)
  }
  .dca-foundation__code .solara-code-highlight__box {
    max-height: 400px;
    overflow: auto;
  }
</style>
