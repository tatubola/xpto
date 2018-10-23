<template>
    <div class="modal fade" :id="modalId" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <slot name="modal-title"></slot>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <slot name="modal-body"></slot>
                </div>
                <div class="modal-footer">
                    <slot name="modal-footer"></slot>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
export default {
  props: [
    'modalId'
  ],
  mounted () {
    $('#' + this.modalId).on('hidden.bs.modal', this.modalClosed)
  },
  methods: {
    modalClosed () {
      this.$emit('modalClosed')
    }
  }
}
</script>
