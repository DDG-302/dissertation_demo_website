<script module>
    import { createApp } from 'https://unpkg.com/petite-vue?module'
    
    function AwesomeFunc(){
        return {
            $template: "#awesometmp",
            awesome: true,
            toggle() {
                this.awesome = !this.awesome
            }
        }
    }

    createApp({
        AwesomeFunc
    }).mount()
</script>

<template id="awesometmp">
  <button @click="toggle">toggle</button>
  <h1 v-if="awesome">Vue is awesome!</h1>
  <h1 v-else>Oh no 😢</h1>
</template>