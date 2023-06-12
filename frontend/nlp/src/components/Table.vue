<template>
  <div>
    <v-table>
      <thead>
        <tr>
          <th class="text-left title-column">title</th>
          <th class="text-left summary-column">summary</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in summaries" :key="item.title">
          <td>{{ item.title }}</td>
          <td>{{ item.summary }}</td>
        </tr>
      </tbody>
    </v-table>
  </div>
</template>

<script setup>
import { watch, reactive } from 'vue';

const props = defineProps({
  title: { type: [String, Array], default: 'Default Title' },
  summary: { type: [String, Array], default: 'Default Summary' }
});

watch(
  () => props.title,
  (newTitles, oldTitles) => {
    if (Array.isArray(newTitles)) {
      for (let i = 0; i < newTitles.length; i++) {
        const newTitle = newTitles[i];
        const newSummary = Array.isArray(props.summary)
          ? props.summary[i]
          : props.summary;
        summaries.push({
          title: newTitle,
          summary: newSummary
        });
      }
    } else {
      summaries.push({
        title: newTitles,
        summary: Array.isArray(props.summary) ? props.summary[0] : props.summary
      });
    }
  },
  { deep: true }
);

const summaries = reactive([]);
</script>

<style scoped>
.title-column {
  width: 30%;
  text-align: center !important;
}

.summary-column {
  width: 70%;
  text-align: center !important;
}
</style>
