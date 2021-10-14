import gzip

# Parsing of the file
def parse_gff(gff_path):

  gene_dict = []
  trans_dict = []
  exon_dict = []

  try:
    #for line in open(gff_path, 'rt'):
    for line in gzip.open(gff_path, 'rt'):

      if line.startswith('#'):
        continue

      # obtain all info of the record
      fields = line.split('\t')
      seqid = fields[0]
      source = fields[1]
      seqtype = fields[2]
      start = int(fields[3])
      end = int(fields[4])
      score = fields[5]
      strand = fields[6]
      phase = fields[7]
      attributes = dict([attribute.split('=') for attribute in fields[-1].strip('\n').split(';')])
       
      # if a record is a gene  
      if 'gene_id' in attributes:
        
        gene_id = attributes['gene_id'].split(':')[-1]
        biotype = attributes['biotype']
        description = attributes.get('description', '')

        gene = {'gene_id': gene_id, 'start': start, 'end': end, 
                'strand': strand, 'biotype': biotype, 
                'description': description}

        gene_dict.append(gene)

        continue
  
      # if the record is a transcript  
      elif 'transcript_id' in attributes:

        trns = attributes['transcript_id'].split(':')[-1]
        gn = attributes['Parent'].split(':')[-1]
        biotype = attributes['biotype']

        transcript = {'trans_id': trns, 'start': start, 'end': end, 
                      'strand': strand, 'biotype': biotype, 'gene': gn}

        trans_dict.append(transcript)

        continue

      # if the record is an exon 
      elif seqtype == 'exon':

        exon_id = attributes['exon_id'].split(':')[-1]
        trns = attributes['Parent'].split(':')[-1]
        exon_len = abs(end-start)

        exon = {'exon_id': exon_id, 'start': start, 'end': end, 
                'exon_length': exon_len, 'strand': strand, 'transcript': trns}

        exon_dict.append(exon)

        continue

      else:
        continue

    return [gene_dict, trans_dict, exon_dict]

  except EOFError:

    err = 'EOFError: Compressed file ended before the end-of-stream marker was reached'
    print('!!! ERROR')
    print('An error happened while parsing the GFF file:')
    print(err)

    with open(config.ERRORLOG_DIR /'ErrorLogGffParsing.txt','a') as errorlog:
      errorlog.write('# ERROR in \n')
      errorlog.write(str(gff_path))
      errorlog.write('\n' + err + '\n')
    errorlog.close()

    return 'BAD-PARSING'