#!/usr/bin/python3
from torrent_parse_and_track import *
from handshake import *
from classes import piece_work
from peer_communication import calculate_bounds_for_piece
from download import *
import argparse
import threading
import queue
import os
import concurrent.futures
import time



# ---------------------------- global Variables --------------------------- #

global_info_hash = ''

work_queue = queue.Queue()
results_queue = queue.Queue()

qlock = threading.Lock()        

# -------------------- Create an ArgumentParser object -------------------- #

parser = argparse.ArgumentParser(description='adding input')
parser.add_argument('--input', '-i', type=str, help='adding input file')
#parser.add_argument('--output', '-o', type=str, help='adding output file')

#use command: ./main -i pg2600.txt.torrent


# ----------------------- Downloader thread method  ----------------------- #

exit_flag = False

def download_thread(peer: Peer):
    print("peer ip: " + str(peer.ip_str_addr) + ":" + str(peer.port))
    try:
        print("doing handshake")
        do_handshake(peer, global_info_hash)
    except socket.error as e:
        print("handshake failed in download thread:" + str(e))
        peer.socket.close()
        return
    #TODO implement downloading loop here
    startDownload(peer, global_info_hash, work_queue, results_queue)

    #done downloading. Clean up
    peer.socket.close()
    return


# ----------------------------- Main Method  ------------------------------ #
if  __name__ == "__main__":
    # Parse the command-line arguments
    args = parser.parse_args()
    input = args.input
    """to test for your liking"""

    #testing parsing
    t = open_file(input)
    #print(t.__dict__)

    #testing tracking
    str1 = 12313 #port
    str2 = "19284102906887310628" #20 characters 
    final_arr = requestPeers(str2, str1, t) #return list of all peers 

    global_info_hash = t.InfoHash

    #set up work queue
    total_size = 0  #total size allocated as work pieces
    for i in range(len(t.PieceHashes)):

        if(total_size + t.PieceLength) > t.Length:
            cur_piece_size = t.Length - total_size 
        else:
            cur_piece_size = t.PieceLength

        piece = piece_work(index=i,
                           hash=t.PieceHashes[i],
                           length=cur_piece_size)
        total_size += piece.length
        work_queue.put(piece)

    #spawn one thread per peer
    threads = []
    thread_no = 1
    for peer in final_arr:
        peer.thread_no = thread_no
        thread_no += 1
        #download_thread(peer)
        thr = threading.Thread(target=download_thread, args=(peer,))
        thr.daemon = True
        thr.start()
        threads.append(thr)


    filename = t.Name
    if os.path.exists(filename):
        print("file already exists, deleting...")
        os.remove(filename)
    output_file = open(filename, 'xb') #x = create a file, b = binary mode

    pieces_complete = 0

    #as results become available, copy them into the file at the correct location
    #continue until all pieces are downloaded
    while pieces_complete < len(t.PieceHashes):
        try:
            with qlock: 
                result = results_queue.get(timeout=.1)
        except queue.Empty as e:
            time.sleep(.1)
            continue
        offset = t.PieceLength * result.index
        output_file.seek(offset)
        output_file.write(result.buf)
        
        pieces_complete += 1

    print("Done downloading " + str(filename))
    #clean up
    output_file.close()
    for thread in threads:
        thread.join()
    


