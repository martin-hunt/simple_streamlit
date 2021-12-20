import streamlit as st
import librosa
from pathlib import Path
import plotly.graph_objs as go
import hashlib
import numpy as np

################ Model ################
class Model:
    header = 'Example Streamlit'

    def __init__(self):
        if 'height' not in st.session_state:
            # initial values for widgets
            self.height = 500
            self.swap = False
            self.color = 'darkgreen'

            # computed values
            self.md5 = b''

            # save files here
            self.temp = Path.cwd() / 'temp'
            self.temp.mkdir(exist_ok=True)
            self.fname = ''
    
    def __getattr__(self, key):
        return st.session_state[key]
    
    def __setattr__(self, key, value):
        st.session_state[key] = value

    def write_file(self):
        print(f"Upload {self.upload}")
        if self.upload is None:
            return
        data = self.upload.getvalue()

        # compute a hash to determine if the file has changed
        md5 = hashlib.md5(data).digest()
        if md5 != self.md5:
            # remove old file
            if self.fname and self.fname.exists():
                self.fname.unlink()
            self.md5 = md5
            self.fname = self.temp / self.upload.name
            print(f'Writing to {self.fname}')
            with open(self.fname, "wb") as f:
                f.write(data)
            # if needed, call function here to recompute things with the new file

    def plot_audio(self):
        adata, sr = librosa.load(self.fname, mono=False, sr=None)
        if len(adata.shape) == 1:
            self.do_plot(adata, sr, '')
        else:
            chan_name = {0: 'Left', 1: 'Right'}
            for channel in range(len(adata.shape)):
                title = f'<b>{chan_name[channel]}</b>'
                self.do_plot(adata[channel], sr, title)

    def do_plot(self, data, sr, title):
        fig = go.Figure()
        psize = int(min(len(data), 5e5))
        x = np.array(range(psize))/sr
        data = data[:psize]
        fig.add_trace(go.Scattergl(x=x, y=data, marker={'color': self.color}))
        if psize == 5e5:
            title += ' (truncated)'
        fig.update_layout(title=title,
                        xaxis_title='Time(s)',
                        height=self.height)
        st.plotly_chart(fig, use_container_width=True)
            
################ View  ################
def view(m):
    st.set_page_config(
        page_title="Example Streamlit",
        page_icon="♾️",
        layout="wide",
    )

    with st.sidebar:
        st.header(m.header)
        st.file_uploader('Upload File', type=['wav', 'flac'], on_change=m.write_file, key='upload')
        st.color_picker('Plot Color', key='color')
        st.slider('Plot Height', key='height', step=10, min_value=400, max_value=1000)
        st.checkbox('Show Audio Widget', key='show_audio')
    
    if m.fname:
        m.plot_audio()
        if m.show_audio:
            st.audio(m.upload.getvalue()[:500000])






################ Start  ################
view(Model())

